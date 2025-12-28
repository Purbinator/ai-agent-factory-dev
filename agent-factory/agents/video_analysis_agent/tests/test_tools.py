"""Tests for agent tools."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

import tools
from dependencies import AgentDependencies
from pydantic_ai import RunContext


class MockRunContext:
    """Mock RunContext for testing."""
    
    def __init__(self, deps):
        self.deps = deps


class TestTools:
    """Test suite for agent tools."""
    
    @pytest.mark.asyncio
    async def test_process_video_with_gemini_success(
        self, 
        mock_dependencies,
        temp_video_path
    ):
        """Test successful Gemini video processing."""
        ctx = MockRunContext(mock_dependencies)
        
        # Mock the processor
        mock_analysis = {
            "patterns": [{"type": "test", "timestamp": "00:01:00"}],
            "timeline": []
        }
        
        with patch('tools.GeminiVideoProcessor') as MockProcessor:
            mock_processor = MockProcessor.return_value
            mock_processor.process_video = AsyncMock(return_value=mock_analysis)
            
            result = await tools.process_video_with_gemini(
                ctx, 
                str(temp_video_path)
            )
        
        assert result["status"] == "success"
        assert "analysis" in result
        assert result["stage"] == "gemini_complete"
    
    @pytest.mark.asyncio
    async def test_process_video_with_gemini_file_not_found(self, mock_dependencies):
        """Test Gemini processing with missing video file."""
        ctx = MockRunContext(mock_dependencies)
        
        result = await tools.process_video_with_gemini(
            ctx,
            "/nonexistent/video.mp4"
        )
        
        assert result["status"] == "error"
        assert "error" in result
        assert result["stage"] == "gemini_failed"
    
    @pytest.mark.asyncio
    async def test_transcribe_with_whisper_success(
        self,
        mock_dependencies,
        temp_video_path
    ):
        """Test successful Whisper transcription."""
        ctx = MockRunContext(mock_dependencies)
        mock_dependencies.set_video_path(str(temp_video_path))
        
        mock_transcript = {
            "text": "Test transcript",
            "segments": [],
            "duration": 120.0
        }
        
        with patch('tools.WhisperTranscriber') as MockTranscriber:
            mock_transcriber = MockTranscriber.return_value
            mock_transcriber.transcribe_video = AsyncMock(return_value=mock_transcript)
            
            result = await tools.transcribe_with_whisper(ctx)
        
        assert result["status"] == "success"
        assert "transcript" in result
        assert result["stage"] == "whisper_complete"
    
    @pytest.mark.asyncio
    async def test_transcribe_with_whisper_no_video_path(self, mock_dependencies):
        """Test Whisper transcription without video path."""
        ctx = MockRunContext(mock_dependencies)
        
        result = await tools.transcribe_with_whisper(ctx)
        
        assert result["status"] == "error"
        assert "No video path" in result["error"]
    
    @pytest.mark.asyncio
    async def test_chunk_video_semantically_success(
        self,
        mock_dependencies,
        sample_gemini_analysis,
        sample_whisper_transcript
    ):
        """Test successful semantic chunking."""
        ctx = MockRunContext(mock_dependencies)
        mock_dependencies.store_gemini_analysis(sample_gemini_analysis)
        mock_dependencies.store_whisper_transcript(sample_whisper_transcript)
        
        with patch('tools.SemanticVideoChunker') as MockChunker:
            mock_chunker = MockChunker.return_value
            mock_segments = [
                Mock(
                    start_time=0.0,
                    end_time=60.0,
                    duration=60.0,
                    segment_type="explanation",
                    primary_pattern=None,
                    key_features=[],
                    transcript_text="",
                    visual_changes=[],
                    timestamp_range="00:00:00 - 00:01:00"
                )
            ]
            mock_chunker.chunk_video = Mock(return_value=mock_segments)
            
            result = await tools.chunk_video_semantically(ctx)
        
        assert result["status"] == "success"
        assert "chunks" in result
        assert result["stage"] == "chunking_complete"
    
    @pytest.mark.asyncio
    async def test_chunk_video_semantically_missing_prerequisites(self, mock_dependencies):
        """Test chunking without prerequisites."""
        ctx = MockRunContext(mock_dependencies)
        
        result = await tools.chunk_video_semantically(ctx)
        
        assert result["status"] == "error"
        assert "Gemini analysis not complete" in result["error"]
    
    @pytest.mark.asyncio
    async def test_build_knowledge_graph_success(
        self,
        mock_dependencies,
        sample_gemini_analysis,
        sample_whisper_transcript,
        sample_semantic_chunks
    ):
        """Test successful knowledge graph building."""
        ctx = MockRunContext(mock_dependencies)
        mock_dependencies.store_gemini_analysis(sample_gemini_analysis)
        mock_dependencies.store_whisper_transcript(sample_whisper_transcript)
        mock_dependencies.store_semantic_chunks(sample_semantic_chunks)
        
        mock_kg = {
            "timeline": [],
            "orderflow_rules": [],
            "pattern_signatures": [],
            "confidence_matrix": {},
            "metadata": {"total_events": 0, "total_rules": 0, "total_patterns": 0}
        }
        
        with patch('tools.KnowledgeGraphBuilder') as MockBuilder:
            mock_builder = MockBuilder.return_value
            mock_builder.build_knowledge_graph = Mock(return_value=mock_kg)
            
            result = await tools.build_knowledge_graph(ctx)
        
        assert result["status"] == "success"
        assert "knowledge_graph" in result
        assert result["stage"] == "knowledge_graph_complete"
    
    @pytest.mark.asyncio
    async def test_build_knowledge_graph_missing_stages(self, mock_dependencies):
        """Test knowledge graph building with missing stages."""
        ctx = MockRunContext(mock_dependencies)
        
        result = await tools.build_knowledge_graph(ctx)
        
        assert result["status"] == "error"
        assert "Missing stages" in result["error"]
        assert "missing_stages" in result
    
    @pytest.mark.asyncio
    async def test_generate_system_prompt_success(
        self,
        mock_dependencies,
        sample_knowledge_graph,
        temp_output_dir
    ):
        """Test successful system prompt generation."""
        ctx = MockRunContext(mock_dependencies)
        mock_dependencies.store_knowledge_graph(sample_knowledge_graph)
        mock_dependencies.settings.output_directory = str(temp_output_dir)
        
        with patch('tools.SystemPromptGenerator') as MockGenerator:
            mock_generator = MockGenerator.return_value
            output_path = temp_output_dir / "system_prompt.txt"
            mock_generator.generate_system_prompt = Mock(return_value=output_path)
            mock_generator.generate_summary_report = Mock(return_value="Summary")
            
            result = await tools.generate_system_prompt(ctx)
        
        assert result["status"] == "success"
        assert "output_path" in result
        assert "summary" in result
        assert result["stage"] == "system_prompt_complete"
    
    @pytest.mark.asyncio
    async def test_generate_system_prompt_no_kg(self, mock_dependencies):
        """Test system prompt generation without knowledge graph."""
        ctx = MockRunContext(mock_dependencies)
        
        result = await tools.generate_system_prompt(ctx)
        
        assert result["status"] == "error"
        assert "Knowledge graph not built" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_full_pipeline_partial_failure(
        self,
        mock_dependencies,
        temp_video_path
    ):
        """Test full pipeline with partial failure."""
        ctx = MockRunContext(mock_dependencies)
        
        # Mock first stage to succeed, second to fail
        with patch('tools.process_video_with_gemini') as mock_gemini:
            mock_gemini.return_value = {
                "status": "success",
                "analysis": {},
                "stage": "gemini_complete"
            }
            
            with patch('tools.transcribe_with_whisper') as mock_whisper:
                mock_whisper.return_value = {
                    "status": "error",
                    "error": "Test error",
                    "stage": "whisper_failed"
                }
                
                result = await tools.run_full_pipeline(ctx, str(temp_video_path))
        
        # Pipeline should return but not complete
        assert "stages" in result
        assert "gemini" in result["stages"]
        assert "whisper" in result["stages"]
        assert result["stages"]["gemini"]["status"] == "success"
        assert result["stages"]["whisper"]["status"] == "error"
