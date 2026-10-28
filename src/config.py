"""Configuration and Environment Settings for Crucible AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current working dir, and also in the project root directory
project_root = Path(__file__).resolve().parent.parent
env_in_root = project_root / ".env"
if env_in_root.exists():
    load_dotenv(dotenv_path=env_in_root)
else:
    load_dotenv()

def get_gemini_api_key(st_context=None) -> str:
    """Retrieve Gemini API key quietly from Streamlit secrets, .env, or environment."""
    if st_context is not None:
        try:
            if "GEMINI_API_KEY" in st_context.secrets:
                return st_context.secrets["GEMINI_API_KEY"].strip(' "\'')
        except Exception:
            pass

    key = os.getenv("GEMINI_API_KEY", "")
    return key.strip(' "\'')

# Default primary model and stable high-limit failover candidates (500 RPD / 15 RPM)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
SUPPORTED_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
]
