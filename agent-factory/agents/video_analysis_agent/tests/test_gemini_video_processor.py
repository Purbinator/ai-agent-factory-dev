"""Tests for Gemini video processor."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import json

from ingestion.video_processor import GeminiVideoProcessor, OrderflowPattern


class TestGeminiVideoProcessor:
    """Test suite for GeminiVideoProcessor."""
    
    def test_initialization(self, mock_gemini_client, mock_settings):
        """Test processor initialization."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        assert processor.client == mock_gemini_client
        assert processor.settings == mock_settings
        assert processor.processing_results == {}
    
    def test_structure_results_with_json(self, mock_gemini_client, mock_settings):
        """Test structuring results from JSON response."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        json_response = """```json
        {
            "patterns": [{"type": "test", "description": "test pattern"}],
            "timeline": []
        }
        ```"""
        
        result = processor._structure_results(json_response)
        
        assert "patterns" in result
        assert len(result["patterns"]) == 1
        assert result["patterns"][0]["type"] == "test"
    
    def test_structure_results_with_text(self, mock_gemini_client, mock_settings):
        """Test structuring results from plain text response."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        text_response = """
        At 00:01:30: DOM imbalance detected
        Pattern: Large buy orders
        Volume surge at 00:02:45
        """
        
        result = processor._structure_results(text_response)
        
        assert "raw_analysis" in result
        assert "patterns" in result
        assert "timeline" in result
    
    def test_extract_patterns(self, mock_gemini_client, mock_settings):
        """Test pattern extraction from text."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        text = """
        Pattern detected: DOM imbalance
        Large volume surge observed
        Order flow changed direction
        """
        
        patterns = processor._extract_patterns(text)
        
        assert len(patterns) > 0
        assert any("pattern" in p["description"].lower() for p in patterns)
    
    def test_extract_timeline(self, mock_gemini_client, mock_settings):
        """Test timeline extraction with timestamps."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        text = """
        At 00:01:30, large orders appeared
        Price broke at 1:45
        Volume increased at 02:30
        """
        
        timeline = processor._extract_timeline(text)
        
        assert len(timeline) >= 2
        assert all("timestamp" in event for event in timeline)
    
    def test_extract_visual_markers(self, mock_gemini_client, mock_settings):
        """Test visual marker extraction."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        text = """
        Cursor points to large bid
        Yellow highlight on chart
        Annotation shows key level
        """
        
        markers = processor._extract_visual_markers(text)
        
        assert len(markers) >= 2
        assert any("cursor" in marker.lower() for marker in markers)
    
    def test_extract_cross_modal_points(self, mock_gemini_client, mock_settings):
        """Test cross-modal validation point extraction."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        text = """
        Visual pattern confirms audio trigger
        This aligns with trader speech
        Verify with audio confirmation
        """
        
        points = processor._extract_cross_modal_points(text)
        
        assert len(points) >= 2
        assert all(p["validation_type"] == "cross_modal" for p in points)
    
    @pytest.mark.asyncio
    async def test_process_video_file_not_found(self, mock_gemini_client, mock_settings):
        """Test error handling for missing video file."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        with pytest.raises(FileNotFoundError):
            await processor.process_video(Path("/nonexistent/video.mp4"))
    
    @pytest.mark.asyncio
    async def test_upload_video(self, mock_gemini_client, mock_settings, temp_video_path):
        """Test video upload to Gemini."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        mock_file = Mock()
        mock_file.name = "test_file"
        mock_file.state = Mock()
        mock_file.state.name = "ACTIVE"
        
        with patch('google.generativeai.upload_file', return_value=mock_file):
            video_file = await processor._upload_video(temp_video_path)
            assert video_file.name == "test_file"
    
    @pytest.mark.asyncio
    async def test_wait_for_processing_success(self, mock_gemini_client, mock_settings):
        """Test waiting for video processing to complete."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        mock_file = Mock()
        mock_file.name = "test_file"
        mock_file.state = Mock()
        mock_file.state.name = "ACTIVE"  # Already processed
        
        # Should not raise
        await processor._wait_for_processing(mock_file)
    
    @pytest.mark.asyncio
    async def test_wait_for_processing_failed(self, mock_gemini_client, mock_settings):
        """Test error handling when video processing fails."""
        processor = GeminiVideoProcessor(mock_gemini_client, mock_settings)
        
        mock_file = Mock()
        mock_file.name = "test_file"
        mock_file.state = Mock()
        mock_file.state.name = "FAILED"
        
        with pytest.raises(RuntimeError, match="Video processing failed"):
            await processor._wait_for_processing(mock_file)
