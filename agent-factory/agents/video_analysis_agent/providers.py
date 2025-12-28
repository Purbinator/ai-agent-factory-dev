"""Model providers for Video Analysis Agent."""

from typing import Optional
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from settings import load_settings
import google.generativeai as genai


def get_llm_model(model_choice: Optional[str] = None) -> OpenAIModel:
    """
    Get LLM model configuration for agent orchestration.
    Supports OpenAI-compatible API providers.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured OpenAI-compatible model
    """
    settings = load_settings()
    
    llm_choice = model_choice or settings.llm_model
    base_url = settings.llm_base_url
    api_key = settings.llm_api_key
    
    # Create provider based on configuration
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    
    return OpenAIModel(llm_choice, provider=provider)


def get_gemini_model(model_choice: Optional[str] = None) -> GeminiModel:
    """
    Get Gemini model for video analysis.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured Gemini model
    """
    settings = load_settings()
    
    model_name = model_choice or settings.gemini_model
    
    # Configure Gemini API
    genai.configure(api_key=settings.gemini_api_key)
    
    return GeminiModel(model_name)


def get_gemini_client():
    """
    Get configured Gemini client for direct API access.
    
    Returns:
        Configured generativeai module
    """
    settings = load_settings()
    genai.configure(api_key=settings.gemini_api_key)
    return genai


def get_model_info() -> dict:
    """
    Get information about current model configuration.
    
    Returns:
        Dictionary with model configuration info
    """
    settings = load_settings()
    
    return {
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "gemini_model": settings.gemini_model,
        "whisper_model": settings.whisper_model,
        "whisper_use_api": settings.whisper_use_api,
    }


def validate_providers() -> bool:
    """
    Validate that all provider configurations are properly set.
    
    Returns:
        True if all providers are valid
    """
    try:
        # Check LLM configuration
        get_llm_model()
        
        # Check Gemini configuration
        get_gemini_client()
        
        return True
    except Exception as e:
        print(f"Provider validation failed: {e}")
        return False
