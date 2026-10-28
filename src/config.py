"""Configuration and Environment Settings for Crucible AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current working dir and project root
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

# Models sorted strictly from highest RPM/RPD at the top to lowest at the end
AVAILABLE_MODELS = [
    {
        "id": "gemini-3.5-flash-lite",
        "label": "Gemini 3.5 Flash Lite — 15 RPM | 500 RPD (Recommended)",
        "rpm": 15,
        "rpd": 500,
    },
    {
        "id": "gemini-3.1-flash-lite",
        "label": "Gemini 3.1 Flash Lite — 15 RPM | 500 RPD",
        "rpm": 15,
        "rpd": 500,
    },
    {
        "id": "gemini-3-flash-preview",
        "label": "Gemini 3 Flash — 5 RPM | 20 RPD",
        "rpm": 5,
        "rpd": 20,
    },
    {
        "id": "gemini-3.8-flash",
        "label": "Gemini 3.8 Flash — 5 RPM | 20 RPD",
        "rpm": 5,
        "rpd": 20,
    },
    {
        "id": "gemini-3.6-flash",
        "label": "Gemini 3.6 Flash — 5 RPM | 20 RPD",
        "rpm": 5,
        "rpd": 20,
    },
    {
        "id": "gemini-robotics-er-2-preview",
        "label": "Gemini Robotics ER 2 — 5 RPM | 20 RPD",
        "rpm": 5,
        "rpd": 20,
    },
]

MODEL_LABEL_TO_ID = {m["label"]: m["id"] for m in AVAILABLE_MODELS}
MODEL_ID_TO_LABEL = {m["id"]: m["label"] for m in AVAILABLE_MODELS}
DEFAULT_MODEL = AVAILABLE_MODELS[0]["id"]
