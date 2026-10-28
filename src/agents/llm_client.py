"""Resilient Gemini LLM Client supporting user-selected models with failover."""

import json
import logging
import random
import time
import requests
from typing import List, Optional

try:
    from src.config import AVAILABLE_MODELS
except (ImportError, AttributeError):
    AVAILABLE_MODELS = [
        {"id": "gemini-3.5-flash-lite", "label": "Gemini 3.5 Flash Lite", "rpm": 15, "rpd": 500},
        {"id": "gemini-3.1-flash-lite", "label": "Gemini 3.1 Flash Lite", "rpm": 15, "rpd": 500},
        {"id": "gemini-3-flash-preview", "label": "Gemini 3 Flash", "rpm": 5, "rpd": 20},
        {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash", "rpm": 5, "rpd": 20},
    ]

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for generating completions using user-selected model with failover."""

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key.strip(' "\'')
        self.model = model or "gemini-3.5-flash-lite"
        
        # Priority order starts with the user's selected model, then remaining models
        self.models_to_try: List[str] = [self.model]
        for m in AVAILABLE_MODELS:
            m_id = m["id"]
            if m_id not in self.models_to_try:
                self.models_to_try.append(m_id)

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate response with exponential backoff and jitter."""
        if not self.api_key:
            return (
                "Error: GEMINI_API_KEY is missing. "
                "Please configure GEMINI_API_KEY in your .env file or environment."
            )

        last_error = ""

        # Try user's selected model first, then fallbacks
        for model_name in self.models_to_try:
            for attempt in range(3):
                res, err, status_code = self._call_rest_api(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature
                )
                if res:
                    return res
                
                last_error = f"{model_name} [{status_code}]: {err}"
                
                if status_code == 404:
                    break

                # Back off on 503 or 429
                if status_code in (503, 429) and attempt < 2:
                    delay = 1.2 * (1.6 ** attempt) + random.uniform(0.2, 0.6)
                    time.sleep(delay)
                    continue

        return f"Unable to generate response. Last API response: {last_error}"

    def _call_rest_api(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float
    ) -> (Optional[str], str, int):
        """Execute HTTP request to Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1500,
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    full_text = "".join(p.get("text", "") for p in parts if "text" in p)
                    if full_text.strip():
                        return full_text.strip(), "", 200
                return None, "Empty text in response", 200
            
            err_msg = resp.text
            try:
                err_json = resp.json()
                err_msg = err_json.get("error", {}).get("message", resp.text)
            except Exception:
                pass
            return None, err_msg, resp.status_code

        except requests.exceptions.Timeout:
            return None, "Request timed out", 408
        except Exception as exc:
            return None, f"Connection error: {str(exc)}", 500
