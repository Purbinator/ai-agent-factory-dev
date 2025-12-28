"""Whisper transcription with word-level timestamps."""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class TranscriptWord:
    """Represents a transcribed word with timing."""
    word: str
    start: float  # seconds
    end: float  # seconds
    confidence: Optional[float] = None


@dataclass
class TranscriptSegment:
    """Represents a transcript segment."""
    text: str
    start: float
    end: float
    words: List[TranscriptWord]


class WhisperTranscriber:
    """
    Transcribe audio using OpenAI Whisper with word-level timestamps.
    
    Supports both local Whisper model and OpenAI API.
    """
    
    def __init__(self, openai_client, settings):
        """
        Initialize transcriber.
        
        Args:
            openai_client: OpenAI async client (for API mode)
            settings: Application settings
        """
        self.client = openai_client
        self.settings = settings
        self.use_api = settings.whisper_use_api
    
    async def transcribe_video(
        self, 
        video_path: Path,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio from video file.
        
        Args:
            video_path: Path to video file
            language: Language code (default from settings)
        
        Returns:
            Dictionary with transcription results
        """
        logger.info(f"Starting Whisper transcription: {video_path}")
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract audio from video
        audio_path = await self._extract_audio(video_path)
        
        try:
            # Transcribe based on mode
            if self.use_api:
                transcript = await self._transcribe_with_api(audio_path, language)
            else:
                transcript = await self._transcribe_with_local(audio_path, language)
            
            # Structure results
            structured = self._structure_transcript(transcript)
            
            logger.info("Transcription complete")
            return structured
            
        finally:
            # Cleanup temporary audio file
            if audio_path.exists():
                audio_path.unlink()
    
    async def _extract_audio(self, video_path: Path) -> Path:
        """
        Extract audio from video using ffmpeg.
        
        Args:
            video_path: Path to video file
        
        Returns:
            Path to extracted audio file
        """
        logger.info("Extracting audio from video...")
        
        # Create temporary audio file
        temp_audio = Path(tempfile.mktemp(suffix=".wav"))
        
        # Reason: Use ffmpeg to extract audio in WAV format for Whisper
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM format
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(temp_audio)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {stderr.decode()}")
        
        logger.info(f"Audio extracted to: {temp_audio}")
        return temp_audio
    
    async def _transcribe_with_api(
        self, 
        audio_path: Path,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe using OpenAI Whisper API.
        
        Args:
            audio_path: Path to audio file
            language: Language code
        
        Returns:
            Transcription results
        """
        logger.info("Transcribing with OpenAI Whisper API...")
        
        lang = language or self.settings.whisper_language
        
        with open(audio_path, "rb") as audio_file:
            # Reason: Use verbose_json to get word-level timestamps
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=lang,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )
        
        return response.model_dump()
    
    async def _transcribe_with_local(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe using local Whisper model.
        
        Args:
            audio_path: Path to audio file
            language: Language code
        
        Returns:
            Transcription results
        """
        logger.info(f"Transcribing with local Whisper ({self.settings.whisper_model})...")
        
        lang = language or self.settings.whisper_language
        
        # Reason: Use whisper CLI with word_timestamps for precision
        cmd = [
            "whisper",
            str(audio_path),
            "--model", self.settings.whisper_model,
            "--language", lang,
            "--output_format", "json",
            "--word_timestamps", "True",
            "--output_dir", str(audio_path.parent)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Whisper CLI failed: {stderr.decode()}")
        
        # Load JSON output
        json_path = audio_path.with_suffix(".json")
        if not json_path.exists():
            raise RuntimeError("Whisper output JSON not found")
        
        with open(json_path, "r") as f:
            result = json.load(f)
        
        # Cleanup
        json_path.unlink()
        
        return result
    
    def _structure_transcript(self, raw_transcript: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure raw transcript into organized format.
        
        Args:
            raw_transcript: Raw transcript from Whisper
        
        Returns:
            Structured transcript dictionary
        """
        segments = []
        
        # Extract segments with word-level timing
        for seg in raw_transcript.get("segments", []):
            words = []
            
            # Extract word-level timestamps if available
            for word_data in seg.get("words", []):
                word = TranscriptWord(
                    word=word_data.get("word", ""),
                    start=word_data.get("start", 0.0),
                    end=word_data.get("end", 0.0),
                    confidence=word_data.get("confidence")
                )
                words.append(word)
            
            segment = TranscriptSegment(
                text=seg.get("text", ""),
                start=seg.get("start", 0.0),
                end=seg.get("end", 0.0),
                words=words
            )
            segments.append(segment)
        
        return {
            "text": raw_transcript.get("text", ""),
            "language": raw_transcript.get("language", ""),
            "duration": raw_transcript.get("duration", 0.0),
            "segments": [self._segment_to_dict(seg) for seg in segments],
            "trader_intent": self._extract_trader_intent(segments),
            "emphasis_patterns": self._extract_emphasis(segments),
            "action_triggers": self._extract_action_triggers(segments),
        }
    
    def _segment_to_dict(self, segment: TranscriptSegment) -> Dict[str, Any]:
        """Convert segment to dictionary."""
        return {
            "text": segment.text,
            "start": segment.start,
            "end": segment.end,
            "timestamp": self._seconds_to_timestamp(segment.start),
            "words": [
                {
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                    "confidence": w.confidence,
                }
                for w in segment.words
            ]
        }
    
    def _extract_trader_intent(
        self, 
        segments: List[TranscriptSegment]
    ) -> List[Dict[str, Any]]:
        """Extract trader intent statements."""
        intent_keywords = ["going to", "will", "plan to", "looking for", "want to", "need to"]
        intents = []
        
        for seg in segments:
            text_lower = seg.text.lower()
            if any(keyword in text_lower for keyword in intent_keywords):
                intents.append({
                    "text": seg.text,
                    "timestamp": self._seconds_to_timestamp(seg.start),
                    "start": seg.start,
                    "end": seg.end,
                })
        
        return intents
    
    def _extract_emphasis(
        self,
        segments: List[TranscriptSegment]
    ) -> List[Dict[str, Any]]:
        """Extract emphasis patterns (repeated words, capitalization)."""
        emphasis = []
        
        for seg in segments:
            # Look for repeated words
            words = [w.word.strip() for w in seg.words]
            for i in range(len(words) - 1):
                if words[i].lower() == words[i + 1].lower():
                    emphasis.append({
                        "type": "repetition",
                        "word": words[i],
                        "timestamp": self._seconds_to_timestamp(seg.start),
                        "start": seg.start,
                    })
        
        return emphasis
    
    def _extract_action_triggers(
        self,
        segments: List[TranscriptSegment]
    ) -> List[Dict[str, Any]]:
        """Extract action trigger phrases."""
        triggers = ["now", "here", "watch this", "look at", "see this", "right here"]
        action_triggers = []
        
        for seg in segments:
            text_lower = seg.text.lower()
            for trigger in triggers:
                if trigger in text_lower:
                    action_triggers.append({
                        "trigger": trigger,
                        "text": seg.text,
                        "timestamp": self._seconds_to_timestamp(seg.start),
                        "start": seg.start,
                        "end": seg.end,
                    })
                    break
        
        return action_triggers
    
    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
