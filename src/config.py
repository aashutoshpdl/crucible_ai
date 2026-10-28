"""Configuration and Environment Settings for Crucible AI."""

import os
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

def get_gemini_api_key(st_context=None) -> str:
    """Retrieve Gemini API key from Streamlit secrets, environment, or .env."""
    # Check Streamlit secrets first (for Cloud deployment)
    if st_context is not None:
        try:
            if "GEMINI_API_KEY" in st_context.secrets:
                return st_context.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

    # Check environment variable or .env
    key = os.getenv("GEMINI_API_KEY", "")
    return key.strip()

# Default model: Google Gemini 2.5 Flash / 2.0 Flash / 1.5 Flash (Generous Free Tier)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

