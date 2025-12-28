"""Tests for video analysis agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from agent import get_video_analysis_agent
from dependencies import AgentDependencies


class TestVideoAnalysisAgent:
    """Test suite for video analysis agent."""
    
    def test_agent_initialization(self, mock_settings):
        """Test that agent is properly initialized."""
        with patch('providers.get_llm_model') as mock_get_model:
            mock_get_model.return_value = Mock()
            agent = get_video_analysis_agent()
            assert agent is not None
    
    def test_agent_has_tools(self, mock_settings):
        """Test that agent has registered tools."""
        with patch('providers.get_llm_model') as mock_get_model:
            mock_get_model.return_value = Mock()
            agent = get_video_analysis_agent()
            
            # Get registered tools
            tools = agent._function_tools
            
            assert len(tools) > 0
            
            # Check for key tools
            tool_names = [tool.name for tool in tools.values()]
            expected_tools = [
                "process_video_with_gemini",
                "transcribe_with_whisper",
                "chunk_video_semantically",
                "build_knowledge_graph",
                "generate_system_prompt",
                "run_full_pipeline"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
    
    @pytest.mark.asyncio
    async def test_agent_deps_type(self, mock_dependencies):
        """Test that agent uses correct dependencies type."""
        # Verify dependencies are of correct type
        assert isinstance(mock_dependencies, AgentDependencies)
    
    def test_agent_system_prompt(self, mock_settings):
        """Test that agent has a system prompt."""
        with patch('providers.get_llm_model') as mock_get_model:
            mock_get_model.return_value = Mock()
            agent = get_video_analysis_agent()
            
            # Agent should have system prompt configured
            assert agent._system_prompt is not None
            prompt_text = str(agent._system_prompt)
            
            # Check for key concepts in system prompt
            assert any(
                keyword in prompt_text.lower()
                for keyword in ["video", "analysis", "knowledge", "extraction"]
            )
