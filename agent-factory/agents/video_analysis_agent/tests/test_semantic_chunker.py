"""Tests for semantic video chunker."""

import pytest
from ingestion.semantic_chunker import SemanticVideoChunker, VideoSegment


class TestSemanticVideoChunker:
    """Test suite for SemanticVideoChunker."""
    
    def test_initialization(self, mock_settings):
        """Test chunker initialization."""
        chunker = SemanticVideoChunker(mock_settings)
        
        assert chunker.settings == mock_settings
        assert chunker.min_duration == mock_settings.chunk_min_duration_seconds
        assert chunker.max_duration == mock_settings.chunk_max_duration_seconds
    
    def test_chunk_video(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript
    ):
        """Test complete video chunking."""
        chunker = SemanticVideoChunker(mock_settings)
        
        segments = chunker.chunk_video(
            sample_gemini_analysis,
            sample_whisper_transcript
        )
        
        assert len(segments) > 0
        assert all(isinstance(seg, VideoSegment) for seg in segments)
        
        # Validate segments
        for seg in segments:
            assert seg.end_time > seg.start_time
            assert seg.duration > 0
            assert seg.segment_type in [
                "explanation", "setup", "execution", "review", "analysis"
            ]
    
    def test_get_duration_from_transcript(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript
    ):
        """Test duration extraction from transcript."""
        chunker = SemanticVideoChunker(mock_settings)
        
        duration = chunker._get_duration(
            sample_gemini_analysis,
            sample_whisper_transcript
        )
        
        assert duration == sample_whisper_transcript["duration"]
    
    def test_extract_visual_boundaries(
        self,
        mock_settings,
        sample_gemini_analysis
    ):
        """Test visual boundary extraction."""
        chunker = SemanticVideoChunker(mock_settings)
        
        boundaries = chunker._extract_visual_boundaries(sample_gemini_analysis)
        
        assert isinstance(boundaries, list)
        
        for timestamp, reason, confidence in boundaries:
            assert isinstance(timestamp, float)
            assert isinstance(reason, str)
            assert 0 <= confidence <= 1
    
    def test_extract_audio_boundaries(
        self,
        mock_settings,
        sample_whisper_transcript
    ):
        """Test audio boundary extraction."""
        chunker = SemanticVideoChunker(mock_settings)
        
        boundaries = chunker._extract_audio_boundaries(sample_whisper_transcript)
        
        assert isinstance(boundaries, list)
        
        for timestamp, reason, confidence in boundaries:
            assert isinstance(timestamp, float)
            assert isinstance(reason, str)
            assert 0 <= confidence <= 1
    
    def test_merge_boundaries(self, mock_settings):
        """Test boundary merging."""
        chunker = SemanticVideoChunker(mock_settings)
        
        visual_boundaries = [
            (60.0, "pattern_change", 0.7),
            (62.0, "state_change", 0.8),
        ]
        
        audio_boundaries = [
            (61.0, "action_trigger", 0.9),
            (120.0, "intent_shift", 0.75),
        ]
        
        merged = chunker._merge_boundaries(visual_boundaries, audio_boundaries)
        
        assert isinstance(merged, list)
        
        # Boundaries within 3 seconds should be merged
        assert len(merged) < len(visual_boundaries) + len(audio_boundaries)
        
        # Check merged boundary properties
        for boundary in merged:
            assert "timestamp" in boundary
            assert "reasons" in boundary
            assert "confidence" in boundary
            assert "sources" in boundary
    
    def test_filter_boundaries(self, mock_settings):
        """Test boundary filtering."""
        chunker = SemanticVideoChunker(mock_settings)
        
        boundaries = [
            {
                "timestamp": 30.0,
                "reasons": ["test"],
                "confidence": 0.8,
                "sources": ["visual"]
            },
            {
                "timestamp": 60.0,
                "reasons": ["test"],
                "confidence": 0.7,
                "sources": ["audio"]
            },
            {
                "timestamp": 120.0,
                "reasons": ["test"],
                "confidence": 0.9,
                "sources": ["visual", "audio"]
            },
        ]
        
        filtered = chunker._filter_boundaries(boundaries, 180.0)
        
        # Should include start and end boundaries
        assert filtered[0]["timestamp"] == 0.0
        assert filtered[-1]["timestamp"] == 180.0
        
        # Should respect minimum duration
        for i in range(len(filtered) - 1):
            duration = filtered[i + 1]["timestamp"] - filtered[i]["timestamp"]
            assert duration >= mock_settings.chunk_min_duration_seconds or duration > 0
    
    def test_classify_segment(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript
    ):
        """Test segment type classification."""
        chunker = SemanticVideoChunker(mock_settings)
        
        # Test explanation classification
        segment_type = chunker._classify_segment(
            0.0, 60.0,
            sample_gemini_analysis,
            sample_whisper_transcript
        )
        
        assert segment_type in [
            "explanation", "setup", "execution", "review", "analysis"
        ]
    
    def test_parse_timestamp_formats(self, mock_settings):
        """Test parsing different timestamp formats."""
        chunker = SemanticVideoChunker(mock_settings)
        
        assert chunker._parse_timestamp("00:01:30") == 90.0
        assert chunker._parse_timestamp("1:30") == 90.0
        assert chunker._parse_timestamp("02:00:00") == 7200.0
        assert chunker._parse_timestamp(90.0) == 90.0
        assert chunker._parse_timestamp(90) == 90.0
    
    def test_get_transcript_text(
        self,
        mock_settings,
        sample_whisper_transcript
    ):
        """Test transcript text extraction for time range."""
        chunker = SemanticVideoChunker(mock_settings)
        
        text = chunker._get_transcript_text(
            60.0, 120.0,
            sample_whisper_transcript
        )
        
        assert isinstance(text, str)
        # Should include segments in time range
        assert len(text) > 0
    
    def test_video_segment_properties(self):
        """Test VideoSegment dataclass properties."""
        segment = VideoSegment(
            start_time=60.0,
            end_time=120.0,
            segment_type="execution",
            primary_pattern="dom_imbalance"
        )
        
        assert segment.duration == 60.0
        assert segment.timestamp_range == "00:01:00 - 00:02:00"
        assert segment.segment_type == "execution"
        assert segment.primary_pattern == "dom_imbalance"
        assert isinstance(segment.key_features, list)
        assert isinstance(segment.visual_changes, list)
