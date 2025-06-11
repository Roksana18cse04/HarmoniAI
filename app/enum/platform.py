from enum import Enum

class Platform(str, Enum):
    """Enum for selecting the LLM platform."""
    GEMINI = "gemini"
    CHATGPT = "chatgpt"
    GROK = "grok"
