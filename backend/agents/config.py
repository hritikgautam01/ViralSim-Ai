"""
ViralSim AI - LLM Configuration & Client Setup
Loads credentials safely from local .env without exposing them.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Look for .env in viralsim-ai root, then parent directory if needed
VIRALSIM_ROOT = Path(__file__).resolve().parent.parent.parent
env_path = VIRALSIM_ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3.5-flash-lite")

def get_llm_client() -> OpenAI:
    """Returns an authenticated OpenAI client configured for Gemini or custom LLM."""
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY is not configured in local .env")
    return OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        timeout=30.0,
        max_retries=2,
    )

def is_llm_available() -> bool:
    """Checks whether the LLM API key is present."""
    return bool(LLM_API_KEY)

