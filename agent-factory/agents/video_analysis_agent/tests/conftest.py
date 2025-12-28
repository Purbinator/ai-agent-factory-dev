"""Pytest configuration and shared fixtures for video analysis agent tests."""

import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import Settings
from dependencies import AgentDependencies


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        gemini_api_key="test-gemini-key",
        gemini_model="gemini-1.5-pro-latest",
        gemini_max_output_tokens=8192,
        gemini_temperature=0.4,
        whisper_api_key="test-whisper-key",
        whisper_model="large-v3",
        whisper_use_api=False,
        whisper_language="en",
        video_fps_extraction=1,
        video_max_duration_minutes=120,
        chunk_similarity_threshold=0.75,
        chunk_min_duration_seconds=5,
        chunk_max_duration_seconds=300,
        clip_model="ViT-B/32",
        use_clip_chunking=True,
        kg_min_pattern_occurrences=2,
        kg_confidence_threshold=0.6,
        output_directory="test_output",
        output_format="json",
        llm_api_key="test-llm-key",
        llm_model="gpt-4o-mini",
        llm_base_url="https://api.openai.com/v1",
        enable_retry=True,
        max_retries=3,
        retry_delay_seconds=5,
    )


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client."""
    client = Mock()
    client.generate_content = Mock(return_value=Mock(text='{"patterns": []}'))
    return client


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    client = AsyncMock()
    client.audio = AsyncMock()
    client.audio.transcriptions = AsyncMock()
    return client


@pytest.fixture
async def mock_dependencies(mock_settings, mock_gemini_client, mock_openai_client):
    """Create mock AgentDependencies."""
    deps = AgentDependencies(
        gemini_client=mock_gemini_client,
        openai_client=mock_openai_client,
        settings=mock_settings
    )
    yield deps
    await deps.cleanup()


@pytest.fixture
def sample_gemini_analysis() -> Dict[str, Any]:
    """Sample Gemini analysis results."""
    return {
        "patterns": [
            {
                "type": "dom_imbalance",
                "timestamp": "00:01:30",
                "description": "Large buy orders at 50000 level",
                "confidence": 0.85,
            },
            {
                "type": "volume_surge",
                "timestamp": "00:02:45",
                "description": "3x average volume on breakout",
                "confidence": 0.92,
            },
        ],
        "timeline": [
            {
                "timestamp": "00:01:00",
                "context": "Market consolidating at resistance",
            },
            {
                "timestamp": "00:02:30",
                "context": "Price breaks above 50000 with volume",
            },
        ],
        "visual_markers": [
            "Cursor pointing to large bid",
            "Yellow highlight on volume bar",
        ],
        "cross_modal_points": [
            {
                "description": "Visual breakout confirms trader verbal trigger",
                "validation_type": "cross_modal",
            }
        ],
    }


@pytest.fixture
def sample_whisper_transcript() -> Dict[str, Any]:
    """Sample Whisper transcription results."""
    return {
        "text": "Watch this level here. Looking for a break above 50000. Now we're seeing volume come in.",
        "language": "en",
        "duration": 180.5,
        "segments": [
            {
                "text": "Watch this level here.",
                "start": 60.0,
                "end": 62.5,
                "timestamp": "00:01:00",
                "words": [
                    {"word": "Watch", "start": 60.0, "end": 60.3, "confidence": 0.95},
                    {"word": "this", "start": 60.3, "end": 60.5, "confidence": 0.96},
                    {"word": "level", "start": 60.5, "end": 60.9, "confidence": 0.94},
                    {"word": "here", "start": 60.9, "end": 62.5, "confidence": 0.93},
                ],
            },
            {
                "text": "Looking for a break above 50000.",
                "start": 90.0,
                "end": 93.0,
                "timestamp": "00:01:30",
                "words": [
                    {"word": "Looking", "start": 90.0, "end": 90.4, "confidence": 0.96},
                    {"word": "for", "start": 90.4, "end": 90.6, "confidence": 0.97},
                    {"word": "a", "start": 90.6, "end": 90.7, "confidence": 0.98},
                    {"word": "break", "start": 90.7, "end": 91.1, "confidence": 0.95},
                ],
            },
        ],
        "trader_intent": [
            {
                "text": "Looking for a break above 50000",
                "timestamp": "00:01:30",
                "start": 90.0,
                "end": 93.0,
            }
        ],
        "emphasis_patterns": [],
        "action_triggers": [
            {
                "trigger": "watch",
                "text": "Watch this level here",
                "timestamp": "00:01:00",
                "start": 60.0,
                "end": 62.5,
            }
        ],
    }


@pytest.fixture
def sample_semantic_chunks() -> list:
    """Sample semantic chunks."""
    return [
        {
            "start_time": 0.0,
            "end_time": 60.0,
            "duration": 60.0,
            "segment_type": "explanation",
            "primary_pattern": None,
            "key_features": ["Market overview", "Setup description"],
            "transcript_text": "Setting up for potential breakout",
            "visual_changes": [],
            "timestamp_range": "00:00:00 - 00:01:00",
        },
        {
            "start_time": 60.0,
            "end_time": 120.0,
            "duration": 60.0,
            "segment_type": "setup",
            "primary_pattern": "dom_imbalance",
            "key_features": ["Large orders appearing", "Spread tightening"],
            "transcript_text": "Watch this level here. Looking for a break",
            "visual_changes": ["DOM imbalance visible"],
            "timestamp_range": "00:01:00 - 00:02:00",
        },
        {
            "start_time": 120.0,
            "end_time": 180.0,
            "duration": 60.0,
            "segment_type": "execution",
            "primary_pattern": "volume_surge",
            "key_features": ["Breakout confirmed", "Volume surge"],
            "transcript_text": "Now we're seeing volume come in",
            "visual_changes": ["Price break", "Volume increase"],
            "timestamp_range": "00:02:00 - 00:03:00",
        },
    ]


@pytest.fixture
def sample_knowledge_graph(sample_gemini_analysis, sample_whisper_transcript, sample_semantic_chunks) -> Dict[str, Any]:
    """Sample knowledge graph."""
    return {
        "timeline": [
            {
                "timestamp": 60.0,
                "timestamp_str": "00:01:00",
                "event_type": "action_trigger",
                "description": "Trigger: watch - Watch this level here",
                "visual_data": None,
                "audio_data": {"trigger": "watch", "text": "Watch this level here"},
                "confidence": 0.9,
            },
            {
                "timestamp": 90.0,
                "timestamp_str": "00:01:30",
                "event_type": "visual_pattern",
                "description": "Large buy orders at 50000 level",
                "visual_data": {"type": "dom_imbalance", "confidence": 0.85},
                "audio_data": None,
                "confidence": 0.8,
            },
        ],
        "orderflow_rules": [
            {
                "rule_id": "RULE_001",
                "description": "Large buy orders at 50000 level",
                "pattern_name": "dom_imbalance",
                "entry_conditions": [],
                "exit_conditions": [],
                "context_requirements": [],
                "success_rate": None,
                "occurrences": 1,
                "confidence": 0.85,
                "examples": [
                    {
                        "timestamp": "00:01:30",
                        "description": "Large buy orders at 50000 level",
                    }
                ],
            }
        ],
        "pattern_signatures": [
            {
                "pattern_id": "PAT_001",
                "pattern_name": "dom_imbalance",
                "visual_characteristics": ["Large buy orders at 50000 level"],
                "audio_confirmations": [],
                "occurrence_count": 1,
                "reliability": 0.1,
                "timestamps": ["00:01:30"],
            }
        ],
        "confidence_matrix": {
            "pattern_only": 0.65,
            "pattern_with_audio": 0.95,
            "multiple_occurrences_bonus": 0.05,
            "context_match_bonus": 0.10,
            "max_confidence": 0.99,
            "average_rule_confidence": 0.85,
            "average_pattern_reliability": 0.1,
            "scoring_examples": [
                {"scenario": "Pattern detected with audio confirmation", "score": 0.95},
                {"scenario": "Pattern detected without audio", "score": 0.65},
            ],
        },
        "metadata": {
            "total_events": 2,
            "total_rules": 1,
            "total_patterns": 1,
        },
    }


@pytest.fixture
def temp_video_path(tmp_path):
    """Create a temporary video file path for testing."""
    video_path = tmp_path / "test_video.mp4"
    video_path.touch()  # Create empty file
    return video_path


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
