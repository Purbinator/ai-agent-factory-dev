"""Tests for Whisper transcriber."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile

from ingestion.transcriber import WhisperTranscriber, TranscriptWord, TranscriptSegment


class TestWhisperTranscriber:
    """Test suite for WhisperTranscriber."""
    
    def test_initialization(self, mock_openai_client, mock_settings):
        """Test transcriber initialization."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        assert transcriber.client == mock_openai_client
        assert transcriber.settings == mock_settings
        assert transcriber.use_api == mock_settings.whisper_use_api
    
    @pytest.mark.asyncio
    async def test_transcribe_video_file_not_found(self, mock_openai_client, mock_settings):
        """Test error handling for missing video file."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        with pytest.raises(FileNotFoundError):
            await transcriber.transcribe_video(Path("/nonexistent/video.mp4"))
    
    @pytest.mark.asyncio
    async def test_extract_audio(self, mock_openai_client, mock_settings, temp_video_path):
        """Test audio extraction from video."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b""))
        mock_process.returncode = 0
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            audio_path = await transcriber._extract_audio(temp_video_path)
            assert audio_path.suffix == ".wav"
            # Cleanup
            if audio_path.exists():
                audio_path.unlink()
    
    @pytest.mark.asyncio
    async def test_extract_audio_ffmpeg_failure(self, mock_openai_client, mock_settings, temp_video_path):
        """Test error handling when ffmpeg fails."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b"ffmpeg error"))
        mock_process.returncode = 1
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            with pytest.raises(RuntimeError, match="ffmpeg failed"):
                await transcriber._extract_audio(temp_video_path)
    
    def test_structure_transcript(self, mock_openai_client, mock_settings):
        """Test transcript structuring."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        raw_transcript = {
            "text": "Watch this level. Looking for break.",
            "language": "en",
            "duration": 120.0,
            "segments": [
                {
                    "text": "Watch this level.",
                    "start": 60.0,
                    "end": 62.5,
                    "words": [
                        {"word": "Watch", "start": 60.0, "end": 60.3, "confidence": 0.95},
                        {"word": "this", "start": 60.3, "end": 60.5, "confidence": 0.96},
                    ]
                }
            ]
        }
        
        structured = transcriber._structure_transcript(raw_transcript)
        
        assert structured["text"] == raw_transcript["text"]
        assert structured["language"] == "en"
        assert structured["duration"] == 120.0
        assert len(structured["segments"]) == 1
        assert "trader_intent" in structured
        assert "emphasis_patterns" in structured
        assert "action_triggers" in structured
    
    def test_extract_trader_intent(self, mock_openai_client, mock_settings):
        """Test trader intent extraction."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        segments = [
            TranscriptSegment(
                text="I'm going to buy here",
                start=60.0,
                end=62.0,
                words=[]
            ),
            TranscriptSegment(
                text="Looking for a break above",
                start=90.0,
                end=93.0,
                words=[]
            ),
            TranscriptSegment(
                text="Market is consolidating",
                start=120.0,
                end=123.0,
                words=[]
            )
        ]
        
        intents = transcriber._extract_trader_intent(segments)
        
        assert len(intents) >= 2
        assert any("going to" in intent["text"].lower() for intent in intents)
    
    def test_extract_emphasis(self, mock_openai_client, mock_settings):
        """Test emphasis pattern extraction."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        segments = [
            TranscriptSegment(
                text="Watch watch this level",
                start=60.0,
                end=62.0,
                words=[
                    TranscriptWord("Watch", 60.0, 60.3),
                    TranscriptWord("watch", 60.3, 60.6),
                    TranscriptWord("this", 60.6, 60.9),
                    TranscriptWord("level", 60.9, 61.2),
                ]
            )
        ]
        
        emphasis = transcriber._extract_emphasis(segments)
        
        assert len(emphasis) >= 1
        assert emphasis[0]["type"] == "repetition"
        assert emphasis[0]["word"].lower() == "watch"
    
    def test_extract_action_triggers(self, mock_openai_client, mock_settings):
        """Test action trigger extraction."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        segments = [
            TranscriptSegment(
                text="Watch this level now",
                start=60.0,
                end=62.0,
                words=[]
            ),
            TranscriptSegment(
                text="Look at the volume here",
                start=90.0,
                end=92.0,
                words=[]
            ),
            TranscriptSegment(
                text="See this breakout pattern",
                start=120.0,
                end=122.0,
                words=[]
            )
        ]
        
        triggers = transcriber._extract_action_triggers(segments)
        
        assert len(triggers) >= 3
        trigger_words = [t["trigger"] for t in triggers]
        assert any(tw in trigger_words for tw in ["watch", "look at", "see this"])
    
    def test_seconds_to_timestamp(self, mock_openai_client, mock_settings):
        """Test timestamp conversion."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        assert transcriber._seconds_to_timestamp(0) == "00:00:00"
        assert transcriber._seconds_to_timestamp(90) == "00:01:30"
        assert transcriber._seconds_to_timestamp(3665) == "01:01:05"
    
    def test_segment_to_dict(self, mock_openai_client, mock_settings):
        """Test segment to dictionary conversion."""
        transcriber = WhisperTranscriber(mock_openai_client, mock_settings)
        
        segment = TranscriptSegment(
            text="Test segment",
            start=60.0,
            end=62.0,
            words=[
                TranscriptWord("Test", 60.0, 60.5, 0.95),
                TranscriptWord("segment", 60.5, 62.0, 0.93),
            ]
        )
        
        seg_dict = transcriber._segment_to_dict(segment)
        
        assert seg_dict["text"] == "Test segment"
        assert seg_dict["start"] == 60.0
        assert seg_dict["end"] == 62.0
        assert seg_dict["timestamp"] == "00:01:00"
        assert len(seg_dict["words"]) == 2
