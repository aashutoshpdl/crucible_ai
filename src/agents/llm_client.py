"""Resilient Gemini LLM Client using High-Limit Models (gemini-3.5-flash-lite: 500 RPD)."""

import json
import logging
import random
import time
import requests
from typing import List, Optional

from src.config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for generating completions with high-limit models and automatic failover."""

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key.strip(' "\'')
        self.model = model or "gemini-3.5-flash-lite"
        
        # Priority order of models: start with high-limit models (500 RPD / 15 RPM)
        self.models_to_try: List[str] = [self.model]
        for m in SUPPORTED_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate response with exponential backoff and jitter."""
        if not self.api_key:
            return (
                "Error: GEMINI_API_KEY is missing. "
                "Please configure GEMINI_API_KEY in your .env file or environment."
            )

        last_error = ""

        # Try models in priority order
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

                # Back off on 503/429
                if status_code in (503, 429) and attempt < 2:
                    delay = 1.5 * (1.7 ** attempt) + random.uniform(0.3, 0.7)
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
        """Execute high-speed HTTP request to Gemini REST API."""
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
