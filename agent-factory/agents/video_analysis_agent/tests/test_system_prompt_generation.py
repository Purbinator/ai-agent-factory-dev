"""Tests for system prompt generator."""

import pytest
from pathlib import Path
import json

from ingestion.system_prompt_generator import SystemPromptGenerator


class TestSystemPromptGenerator:
    """Test suite for SystemPromptGenerator."""
    
    def test_initialization(self, mock_settings, temp_output_dir):
        """Test generator initialization."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        assert generator.settings == mock_settings
        assert generator.output_dir.exists()
    
    def test_generate_system_prompt(
        self, 
        mock_settings, 
        sample_knowledge_graph,
        temp_output_dir
    ):
        """Test system prompt generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        output_path = generator.generate_system_prompt(
            sample_knowledge_graph,
            "/test/video.mp4",
            "test_prompt.txt"
        )
        
        assert output_path.exists()
        assert output_path.name == "test_prompt.txt"
        
        # Check content
        with open(output_path, "r") as f:
            content = f.read()
        
        assert "Trading System Prompt" in content
        assert "OVERVIEW" in content
        assert "CORE TRADING RULES" in content or "CORE RULES" in content
        assert "PATTERN LIBRARY" in content
        
        # Check JSON file was also created
        json_path = output_path.with_suffix(".json")
        assert json_path.exists()
        
        with open(json_path, "r") as f:
            json_data = json.load(f)
        
        assert "timeline" in json_data
        assert "orderflow_rules" in json_data
    
    def test_generate_header(self, mock_settings, temp_output_dir):
        """Test header generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        header = generator._generate_header("/path/to/test_video.mp4")
        
        assert "Trading System Prompt" in header
        assert "test_video.mp4" in header
        assert "Generated from:" in header
        assert "Date:" in header
    
    def test_generate_overview(self, mock_settings, sample_knowledge_graph, temp_output_dir):
        """Test overview generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        overview = generator._generate_overview(sample_knowledge_graph)
        
        assert "OVERVIEW" in overview
        assert str(sample_knowledge_graph["metadata"]["total_events"]) in overview
        assert str(sample_knowledge_graph["metadata"]["total_rules"]) in overview
    
    def test_generate_timeline_reference(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test timeline reference generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        timeline_ref = generator._generate_timeline_reference(sample_knowledge_graph)
        
        assert "TIMELINE REFERENCE" in timeline_ref
        assert "Key moments" in timeline_ref
        
        # Should include high confidence events
        for event in sample_knowledge_graph["timeline"]:
            if event["confidence"] >= 0.8:
                # Check if event is mentioned (could be truncated)
                assert any(
                    part in timeline_ref 
                    for part in [event["timestamp_str"], event["event_type"]]
                )
    
    def test_generate_core_rules(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test core rules generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        rules_section = generator._generate_core_rules(sample_knowledge_graph)
        
        assert "CORE" in rules_section and "RULES" in rules_section
        
        # Should include all rules
        for rule in sample_knowledge_graph["orderflow_rules"]:
            assert rule["rule_id"] in rules_section
            assert str(rule["confidence"]) in rules_section or f"{rule['confidence']:.2f}" in rules_section
    
    def test_generate_pattern_library(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test pattern library generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        pattern_lib = generator._generate_pattern_library(sample_knowledge_graph)
        
        assert "PATTERN LIBRARY" in pattern_lib
        
        # Should include all patterns
        for pattern in sample_knowledge_graph["pattern_signatures"]:
            assert pattern["pattern_id"] in pattern_lib
            assert str(pattern["reliability"]) in pattern_lib or f"{pattern['reliability']:.2f}" in pattern_lib
    
    def test_generate_decision_framework(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test decision framework generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        framework = generator._generate_decision_framework(sample_knowledge_graph)
        
        assert "DECISION FRAMEWORK" in framework
        assert "Confidence" in framework
        
        cm = sample_knowledge_graph["confidence_matrix"]
        assert str(cm["pattern_only"]) in framework or f"{cm['pattern_only']:.2f}" in framework
        assert str(cm["pattern_with_audio"]) in framework or f"{cm['pattern_with_audio']:.2f}" in framework
    
    def test_generate_risk_management(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test risk management section generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        risk_mgmt = generator._generate_risk_management(sample_knowledge_graph)
        
        assert "RISK MANAGEMENT" in risk_mgmt
        assert any(
            keyword in risk_mgmt.lower() 
            for keyword in ["risk", "stop", "position", "size"]
        )
    
    def test_generate_summary_report(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test summary report generation."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        summary = generator.generate_summary_report(sample_knowledge_graph)
        
        assert "Summary Report" in summary
        assert "Extraction Results" in summary
        assert str(sample_knowledge_graph["metadata"]["total_events"]) in summary
        assert str(sample_knowledge_graph["metadata"]["total_rules"]) in summary
    
    def test_output_files_created(
        self, 
        mock_settings, 
        sample_knowledge_graph, 
        temp_output_dir
    ):
        """Test that both TXT and JSON output files are created."""
        mock_settings.output_directory = str(temp_output_dir)
        generator = SystemPromptGenerator(mock_settings)
        
        output_path = generator.generate_system_prompt(
            sample_knowledge_graph,
            "/test/video.mp4",
            "output.txt"
        )
        
        txt_path = temp_output_dir / "output.txt"
        json_path = temp_output_dir / "output.json"
        
        assert txt_path.exists()
        assert json_path.exists()
        
        # Verify JSON is valid
        with open(json_path, "r") as f:
            json_data = json.load(f)
        
        assert json_data == sample_knowledge_graph
