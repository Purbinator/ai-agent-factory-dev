"""Video Analysis Agent - Lossless video knowledge extraction using Gemini & Whisper."""

from .agent import get_video_analysis_agent
from .dependencies import AgentDependencies
from .settings import load_settings

__version__ = "1.0.0"

__all__ = [
    "get_video_analysis_agent",
    "AgentDependencies",
    "load_settings",
]
