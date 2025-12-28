"""Tests for knowledge graph builder."""

import pytest
from ingestion.knowledge_graph_builder import (
    KnowledgeGraphBuilder,
    TimelineEvent,
    OrderflowRule,
    PatternSignature,
    ConfidenceMatrix
)


class TestKnowledgeGraphBuilder:
    """Test suite for KnowledgeGraphBuilder."""
    
    def test_initialization(self, mock_settings):
        """Test builder initialization."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        assert builder.settings == mock_settings
        assert builder.min_occurrences == mock_settings.kg_min_pattern_occurrences
        assert builder.confidence_threshold == mock_settings.kg_confidence_threshold
    
    def test_build_knowledge_graph(
        self, 
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript,
        sample_semantic_chunks
    ):
        """Test complete knowledge graph building."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        kg = builder.build_knowledge_graph(
            sample_gemini_analysis,
            sample_whisper_transcript,
            sample_semantic_chunks
        )
        
        assert "timeline" in kg
        assert "orderflow_rules" in kg
        assert "pattern_signatures" in kg
        assert "confidence_matrix" in kg
        assert "metadata" in kg
        
        metadata = kg["metadata"]
        assert metadata["total_events"] > 0
        assert metadata["total_rules"] >= 0
        assert metadata["total_patterns"] >= 0
    
    def test_build_timeline(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript,
        sample_semantic_chunks
    ):
        """Test timeline building."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        timeline = builder._build_timeline(
            sample_gemini_analysis,
            sample_whisper_transcript,
            sample_semantic_chunks
        )
        
        assert len(timeline) > 0
        assert all(isinstance(event, TimelineEvent) for event in timeline)
        
        # Check chronological order
        for i in range(len(timeline) - 1):
            assert timeline[i].timestamp <= timeline[i + 1].timestamp
    
    def test_extract_rules(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript,
        sample_semantic_chunks
    ):
        """Test rule extraction."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        rules = builder._extract_rules(
            sample_gemini_analysis,
            sample_whisper_transcript,
            sample_semantic_chunks
        )
        
        assert isinstance(rules, list)
        
        for rule in rules:
            assert isinstance(rule, OrderflowRule)
            assert rule.confidence >= builder.confidence_threshold
            assert rule.occurrences >= builder.min_occurrences
    
    def test_build_pattern_signatures(
        self,
        mock_settings,
        sample_gemini_analysis,
        sample_whisper_transcript
    ):
        """Test pattern signature building."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        signatures = builder._build_pattern_signatures(
            sample_gemini_analysis,
            sample_whisper_transcript
        )
        
        assert isinstance(signatures, list)
        
        for sig in signatures:
            assert isinstance(sig, PatternSignature)
            assert sig.occurrence_count >= builder.min_occurrences
            assert 0 <= sig.reliability <= 1
    
    def test_build_confidence_matrix(self, mock_settings):
        """Test confidence matrix building."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        rules = [
            OrderflowRule(
                rule_id="RULE_001",
                description="Test rule",
                pattern_name="test_pattern",
                confidence=0.85
            )
        ]
        
        signatures = [
            PatternSignature(
                pattern_id="PAT_001",
                pattern_name="test_pattern",
                reliability=0.75
            )
        ]
        
        matrix = builder._build_confidence_matrix(rules, signatures)
        
        assert "pattern_only" in matrix
        assert "pattern_with_audio" in matrix
        assert "multiple_occurrences_bonus" in matrix
        assert "context_match_bonus" in matrix
        assert "max_confidence" in matrix
        assert "average_rule_confidence" in matrix
        assert "average_pattern_reliability" in matrix
        assert "scoring_examples" in matrix
        
        # Validate ranges
        assert 0 <= matrix["pattern_only"] <= 1
        assert 0 <= matrix["pattern_with_audio"] <= 1
        assert matrix["pattern_with_audio"] > matrix["pattern_only"]
    
    def test_merge_timeline_events(self, mock_settings):
        """Test merging of nearby timeline events."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        events = [
            TimelineEvent(
                timestamp=60.0,
                timestamp_str="00:01:00",
                event_type="visual",
                description="Visual event",
                confidence=0.8
            ),
            TimelineEvent(
                timestamp=61.5,
                timestamp_str="00:01:01",
                event_type="audio",
                description="Audio event",
                confidence=0.9
            ),
            TimelineEvent(
                timestamp=120.0,
                timestamp_str="00:02:00",
                event_type="visual",
                description="Separate event",
                confidence=0.85
            ),
        ]
        
        merged = builder._merge_timeline_events(events)
        
        # Events within 2 seconds should be merged
        assert len(merged) == 2
        assert merged[0].event_type == "merged_event"
        assert merged[0].confidence == 0.9  # Highest confidence
    
    def test_parse_timestamp_formats(self, mock_settings):
        """Test parsing different timestamp formats."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        assert builder._parse_timestamp("00:01:30") == 90.0
        assert builder._parse_timestamp("1:30") == 90.0
        assert builder._parse_timestamp("02:00:00") == 7200.0
        assert builder._parse_timestamp(90.0) == 90.0
        assert builder._parse_timestamp(90) == 90.0
    
    def test_seconds_to_timestamp(self, mock_settings):
        """Test seconds to timestamp conversion."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        assert builder._seconds_to_timestamp(0) == "00:00:00"
        assert builder._seconds_to_timestamp(90) == "00:01:30"
        assert builder._seconds_to_timestamp(3665) == "01:01:05"
    
    def test_event_to_dict(self, mock_settings):
        """Test event to dictionary conversion."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        event = TimelineEvent(
            timestamp=60.0,
            timestamp_str="00:01:00",
            event_type="test",
            description="Test event",
            visual_data={"key": "value"},
            audio_data={"audio_key": "audio_value"},
            confidence=0.85
        )
        
        event_dict = builder._event_to_dict(event)
        
        assert event_dict["timestamp"] == 60.0
        assert event_dict["timestamp_str"] == "00:01:00"
        assert event_dict["event_type"] == "test"
        assert event_dict["description"] == "Test event"
        assert event_dict["visual_data"]["key"] == "value"
        assert event_dict["audio_data"]["audio_key"] == "audio_value"
        assert event_dict["confidence"] == 0.85
    
    def test_rule_to_dict(self, mock_settings):
        """Test rule to dictionary conversion."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        rule = OrderflowRule(
            rule_id="RULE_001",
            description="Test rule",
            pattern_name="test_pattern",
            occurrences=3,
            confidence=0.85
        )
        
        rule_dict = builder._rule_to_dict(rule)
        
        assert rule_dict["rule_id"] == "RULE_001"
        assert rule_dict["description"] == "Test rule"
        assert rule_dict["pattern_name"] == "test_pattern"
        assert rule_dict["occurrences"] == 3
        assert rule_dict["confidence"] == 0.85
    
    def test_signature_to_dict(self, mock_settings):
        """Test signature to dictionary conversion."""
        builder = KnowledgeGraphBuilder(mock_settings)
        
        signature = PatternSignature(
            pattern_id="PAT_001",
            pattern_name="test_pattern",
            visual_characteristics=["visual1", "visual2"],
            audio_confirmations=["audio1"],
            occurrence_count=5,
            reliability=0.75
        )
        
        sig_dict = builder._signature_to_dict(signature)
        
        assert sig_dict["pattern_id"] == "PAT_001"
        assert sig_dict["pattern_name"] == "test_pattern"
        assert len(sig_dict["visual_characteristics"]) == 2
        assert len(sig_dict["audio_confirmations"]) == 1
        assert sig_dict["occurrence_count"] == 5
        assert sig_dict["reliability"] == 0.75
