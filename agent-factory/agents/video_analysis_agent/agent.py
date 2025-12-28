"""Main agent implementation for Video Analysis."""

from pydantic_ai import Agent
from typing import Optional

from dependencies import AgentDependencies
from prompts import MAIN_SYSTEM_PROMPT
from tools import (
    process_video_with_gemini,
    transcribe_with_whisper,
    chunk_video_semantically,
    build_knowledge_graph,
    generate_system_prompt,
    run_full_pipeline
)

# Lazy initialization to avoid loading settings at import time
_video_analysis_agent: Optional[Agent] = None


def get_video_analysis_agent() -> Agent:
    """
    Get or create the video analysis agent.
    
    Returns:
        Configured Agent instance
    """
    global _video_analysis_agent
    
    if _video_analysis_agent is None:
        from providers import get_llm_model
        
        # Initialize the video analysis agent
        _video_analysis_agent = Agent(
            get_llm_model(),
            deps_type=AgentDependencies,
            system_prompt=MAIN_SYSTEM_PROMPT
        )
        
        # Register processing tools
        _video_analysis_agent.tool(process_video_with_gemini)
        _video_analysis_agent.tool(transcribe_with_whisper)
        _video_analysis_agent.tool(chunk_video_semantically)
        _video_analysis_agent.tool(build_knowledge_graph)
        _video_analysis_agent.tool(generate_system_prompt)
        _video_analysis_agent.tool(run_full_pipeline)
    
    return _video_analysis_agent


# For backward compatibility
video_analysis_agent = property(lambda self: get_video_analysis_agent())
