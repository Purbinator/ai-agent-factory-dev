"""Settings configuration for Video Analysis Agent."""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Gemini Configuration
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key for video analysis"
    )
    
    gemini_model: str = Field(
        default="gemini-1.5-pro-latest",
        description="Gemini model to use for video processing"
    )
    
    gemini_max_output_tokens: int = Field(
        default=8192,
        description="Maximum output tokens for Gemini responses"
    )
    
    gemini_temperature: float = Field(
        default=0.4,
        description="Temperature for Gemini generation (0-1)"
    )
    
    # Whisper Configuration
    whisper_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for Whisper transcription (if using API)"
    )
    
    whisper_model: str = Field(
        default="large-v3",
        description="Whisper model size (tiny, base, small, medium, large, large-v3)"
    )
    
    whisper_use_api: bool = Field(
        default=False,
        description="Use OpenAI API for Whisper (True) or local model (False)"
    )
    
    whisper_language: str = Field(
        default="en",
        description="Language code for transcription"
    )
    
    # Video Processing Configuration
    video_fps_extraction: int = Field(
        default=1,
        description="Frames per second to extract for analysis"
    )
    
    video_max_duration_minutes: int = Field(
        default=120,
        description="Maximum video duration in minutes"
    )
    
    # Semantic Chunking Configuration
    chunk_similarity_threshold: float = Field(
        default=0.75,
        description="Similarity threshold for semantic boundaries (0-1)"
    )
    
    chunk_min_duration_seconds: int = Field(
        default=5,
        description="Minimum chunk duration in seconds"
    )
    
    chunk_max_duration_seconds: int = Field(
        default=300,
        description="Maximum chunk duration in seconds"
    )
    
    # CLIP Configuration (optional for semantic chunking)
    clip_model: str = Field(
        default="ViT-B/32",
        description="CLIP model for visual embeddings"
    )
    
    use_clip_chunking: bool = Field(
        default=True,
        description="Use CLIP embeddings for semantic chunking"
    )
    
    # Knowledge Graph Configuration
    kg_min_pattern_occurrences: int = Field(
        default=2,
        description="Minimum occurrences to include pattern in KG"
    )
    
    kg_confidence_threshold: float = Field(
        default=0.6,
        description="Minimum confidence for rule inclusion (0-1)"
    )
    
    # Output Configuration
    output_directory: str = Field(
        default="output",
        description="Directory for generated outputs"
    )
    
    output_format: str = Field(
        default="json",
        description="Output format (json, yaml, txt)"
    )
    
    # LLM Configuration (for agent orchestration)
    llm_api_key: str = Field(
        ...,
        description="API key for LLM orchestration (OpenAI, Anthropic, etc.)"
    )
    
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="LLM model for agent orchestration"
    )
    
    llm_base_url: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="Base URL for LLM API"
    )
    
    # Processing Configuration
    enable_retry: bool = Field(
        default=True,
        description="Enable retry logic for API failures"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for API calls"
    )
    
    retry_delay_seconds: int = Field(
        default=5,
        description="Delay between retries in seconds"
    )


def load_settings() -> Settings:
    """
    Load settings with proper error handling.
    
    Returns:
        Settings: Configured settings instance
        
    Raises:
        ValueError: If required settings are missing
    """
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "gemini_api_key" in str(e).lower():
            error_msg += "\nMake sure to set GEMINI_API_KEY in your .env file"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        raise ValueError(error_msg) from e
