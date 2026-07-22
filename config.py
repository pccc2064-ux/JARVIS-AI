"""
config.py
---------
Central place to load API keys and settings.

Never hard-code API keys in source files. Set them as environment
variables (recommended) or in a local `.env` file (see `.env.example`).

Required environment variables (set only the ones you plan to use):
    OPENAI_API_KEY      -> for ChatGPT / OpenAI models
    ANTHROPIC_API_KEY   -> for Claude models
    GOOGLE_API_KEY       -> for Gemini (Google Generative AI) models
"""

import os

# Optional: load a local .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Default models — change these to whatever versions you have access to.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Text-to-speech engine: "pyttsx3" (offline, no API key) or "gtts" (Google TTS, needs internet)
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")

# Speech-to-text engine: "google" (free, uses SpeechRecognition's built-in Google Web Speech API,
# no key needed for light use) or "whisper" (OpenAI Whisper API, needs OPENAI_API_KEY)
STT_ENGINE = os.getenv("STT_ENGINE", "google")


def check_keys(providers):
    """Warn (don't crash) if a requested provider's key is missing."""
    missing = []
    if "openai" in providers and not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if "claude" in providers and not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if "gemini" in providers and not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")
    if missing:
        print(f"[config] Warning: missing environment variables: {', '.join(missing)}")
    return missing
