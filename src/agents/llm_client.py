"""Gemini LLM Client with dual support for official SDK and direct REST fallback."""

import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for generating completions using Google Gemini's 100% Free Tier API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key.strip()
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate response from Gemini given a system persona and user prompt."""
        if not self.api_key:
            return (
                "⚠️ Error: Gemini API key is missing. "
                "Please enter your key in the sidebar or set GEMINI_API_KEY in your .env file."
            )

        # 1. Try official google-genai SDK if available
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            )
            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
        except ImportError:
            # SDK not installed; fall through to REST API
            pass
        except Exception as e:
            logger.info(f"SDK call failed with: {e}. Falling back to REST API.")

        # 2. Resilient Direct REST API Fallback (Works with just the 'requests' library)
        return self._generate_rest(system_prompt, user_prompt, temperature)

    def _generate_rest(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Direct HTTP call to Google Generative Language REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
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
                "maxOutputTokens": 2048,
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                return "Received empty response from Gemini model."
            elif resp.status_code == 404 and "gemini-2.5-flash" in self.model:
                # If 2.5 is not yet enabled on the key, fallback to gemini-1.5-flash
                self.model = "gemini-1.5-flash"
                return self._generate_rest(system_prompt, user_prompt, temperature)
            else:
                err_detail = resp.text
                try:
                    err_json = resp.json()
                    err_detail = err_json.get("error", {}).get("message", resp.text)
                except Exception:
                    pass
                return f"Gemini API Error ({resp.status_code}): {err_detail}"
        except requests.exceptions.Timeout:
            return "Request to Gemini API timed out. Please try again."
        except Exception as exc:
            return f"Failed to connect to Gemini API: {str(exc)}"

