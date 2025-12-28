"""Semantic video chunking using intelligent segmentation."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VideoSegment:
    """Represents a semantic video segment."""
    start_time: float  # seconds
    end_time: float  # seconds
    segment_type: str  # explanation, setup, execution, review
    primary_pattern: Optional[str] = None
    key_features: List[str] = None
    transcript_text: Optional[str] = None
    visual_changes: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.key_features is None:
            self.key_features = []
        if self.visual_changes is None:
            self.visual_changes = []
    
    @property
    def duration(self) -> float:
        """Get segment duration in seconds."""
        return self.end_time - self.start_time
    
    @property
    def timestamp_range(self) -> str:
        """Get timestamp range as string."""
        return f"{self._format_time(self.start_time)} - {self._format_time(self.end_time)}"
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class SemanticVideoChunker:
    """
    Intelligent video segmentation based on orderflow state changes.
    
    Identifies segment boundaries using:
    - Visual pattern changes (from Gemini analysis)
    - Trader behavior shifts (from transcript)
    - Audio-visual alignment points
    """
    
    def __init__(self, settings):
        """
        Initialize semantic chunker.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.min_duration = settings.chunk_min_duration_seconds
        self.max_duration = settings.chunk_max_duration_seconds
    
    def chunk_video(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any],
        video_duration: Optional[float] = None
    ) -> List[VideoSegment]:
        """
        Chunk video into semantic segments.
        
        Args:
            gemini_analysis: Results from Gemini video analysis
            whisper_transcript: Results from Whisper transcription
            video_duration: Total video duration in seconds (auto-detect if None)
        
        Returns:
            List of video segments
        """
        logger.info("Starting semantic video chunking...")
        
        # Get video duration
        duration = video_duration or self._get_duration(gemini_analysis, whisper_transcript)
        
        # Extract boundary candidates from both sources
        visual_boundaries = self._extract_visual_boundaries(gemini_analysis)
        audio_boundaries = self._extract_audio_boundaries(whisper_transcript)
        
        # Merge and score boundaries
        merged_boundaries = self._merge_boundaries(visual_boundaries, audio_boundaries)
        
        # Filter and validate boundaries
        final_boundaries = self._filter_boundaries(merged_boundaries, duration)
        
        # Create segments from boundaries
        segments = self._create_segments(final_boundaries, gemini_analysis, whisper_transcript)
        
        logger.info(f"Created {len(segments)} semantic segments")
        return segments
    
    def _get_duration(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any]
    ) -> float:
        """Get video duration from available data."""
        # Try transcript duration first
        if "duration" in whisper_transcript:
            return whisper_transcript["duration"]
        
        # Try to extract from Gemini timeline
        timeline = gemini_analysis.get("timeline", [])
        if timeline:
            max_timestamp = max(
                self._parse_timestamp(event.get("timestamp", "0:00"))
                for event in timeline
            )
            return max_timestamp
        
        # Default fallback
        logger.warning("Could not determine video duration, using 3600s default")
        return 3600.0
    
    def _extract_visual_boundaries(
        self,
        gemini_analysis: Dict[str, Any]
    ) -> List[Tuple[float, str, float]]:
        """
        Extract boundary candidates from visual analysis.
        
        Returns:
            List of (timestamp, reason, confidence) tuples
        """
        boundaries = []
        
        # Extract from patterns
        patterns = gemini_analysis.get("patterns", [])
        for pattern in patterns:
            if "timestamp" in pattern:
                timestamp = self._parse_timestamp(pattern["timestamp"])
                boundaries.append((
                    timestamp,
                    f"pattern_change: {pattern.get('description', 'unknown')}",
                    0.7
                ))
        
        # Extract from timeline events
        timeline = gemini_analysis.get("timeline", [])
        for i, event in enumerate(timeline):
            if "timestamp" in event:
                timestamp = self._parse_timestamp(event["timestamp"])
                context = event.get("context", "")
                
                # Reason: Identify state changes from context
                if any(keyword in context.lower() for keyword in 
                       ["imbalance", "break", "surge", "shift", "change"]):
                    boundaries.append((
                        timestamp,
                        f"state_change: {context[:50]}",
                        0.8
                    ))
        
        return boundaries
    
    def _extract_audio_boundaries(
        self,
        whisper_transcript: Dict[str, Any]
    ) -> List[Tuple[float, str, float]]:
        """
        Extract boundary candidates from audio transcription.
        
        Returns:
            List of (timestamp, reason, confidence) tuples
        """
        boundaries = []
        
        # Extract from action triggers
        triggers = whisper_transcript.get("action_triggers", [])
        for trigger in triggers:
            boundaries.append((
                trigger["start"],
                f"action_trigger: {trigger['trigger']}",
                0.9
            ))
        
        # Extract from trader intent statements
        intents = whisper_transcript.get("trader_intent", [])
        for intent in intents:
            boundaries.append((
                intent["start"],
                f"intent_shift: {intent['text'][:50]}",
                0.75
            ))
        
        # Extract from segment boundaries (natural pauses)
        segments = whisper_transcript.get("segments", [])
        for i in range(len(segments) - 1):
            current_end = segments[i]["end"]
            next_start = segments[i + 1]["start"]
            
            # Reason: Significant pauses indicate topic changes
            gap = next_start - current_end
            if gap > 2.0:  # 2+ second pause
                boundaries.append((
                    current_end,
                    "pause_boundary",
                    0.6
                ))
        
        return boundaries
    
    def _merge_boundaries(
        self,
        visual_boundaries: List[Tuple[float, str, float]],
        audio_boundaries: List[Tuple[float, str, float]]
    ) -> List[Dict[str, Any]]:
        """
        Merge visual and audio boundaries with scoring.
        
        Args:
            visual_boundaries: Boundaries from visual analysis
            audio_boundaries: Boundaries from audio analysis
        
        Returns:
            List of merged boundary dictionaries
        """
        all_boundaries = []
        
        # Add all boundaries
        for timestamp, reason, confidence in visual_boundaries:
            all_boundaries.append({
                "timestamp": timestamp,
                "reasons": [reason],
                "confidence": confidence,
                "sources": ["visual"]
            })
        
        for timestamp, reason, confidence in audio_boundaries:
            all_boundaries.append({
                "timestamp": timestamp,
                "reasons": [reason],
                "confidence": confidence,
                "sources": ["audio"]
            })
        
        # Sort by timestamp
        all_boundaries.sort(key=lambda x: x["timestamp"])
        
        # Merge nearby boundaries (within 3 seconds)
        merged = []
        i = 0
        while i < len(all_boundaries):
            current = all_boundaries[i]
            cluster = [current]
            
            # Reason: Group boundaries that occur within 3 seconds
            j = i + 1
            while j < len(all_boundaries):
                if all_boundaries[j]["timestamp"] - current["timestamp"] <= 3.0:
                    cluster.append(all_boundaries[j])
                    j += 1
                else:
                    break
            
            # Merge cluster
            if len(cluster) > 1:
                merged_boundary = {
                    "timestamp": np.mean([b["timestamp"] for b in cluster]),
                    "reasons": sum([b["reasons"] for b in cluster], []),
                    "confidence": max(b["confidence"] for b in cluster),
                    "sources": list(set(sum([b["sources"] for b in cluster], []))),
                    "cluster_size": len(cluster)
                }
                # Reason: Cross-modal boundaries get confidence boost
                if len(merged_boundary["sources"]) > 1:
                    merged_boundary["confidence"] = min(1.0, merged_boundary["confidence"] * 1.2)
                merged.append(merged_boundary)
            else:
                merged.append(current)
            
            i = j if j > i + 1 else i + 1
        
        return merged
    
    def _filter_boundaries(
        self,
        boundaries: List[Dict[str, Any]],
        video_duration: float
    ) -> List[Dict[str, Any]]:
        """
        Filter boundaries based on confidence and duration constraints.
        
        Args:
            boundaries: Merged boundaries
            video_duration: Total video duration
        
        Returns:
            Filtered boundaries
        """
        # Sort by confidence
        boundaries.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Always include start and end
        filtered = [
            {"timestamp": 0.0, "reasons": ["video_start"], "confidence": 1.0, "sources": ["system"]},
        ]
        
        for boundary in boundaries:
            timestamp = boundary["timestamp"]
            
            # Check if adding this boundary creates valid segments
            prev_timestamp = filtered[-1]["timestamp"]
            duration_from_prev = timestamp - prev_timestamp
            
            # Enforce minimum duration
            if duration_from_prev < self.min_duration:
                continue
            
            # Enforce maximum duration (must split if exceeded)
            if duration_from_prev > self.max_duration:
                # Add intermediate boundary
                mid_timestamp = prev_timestamp + self.max_duration
                filtered.append({
                    "timestamp": mid_timestamp,
                    "reasons": ["max_duration_split"],
                    "confidence": 1.0,
                    "sources": ["system"]
                })
            
            filtered.append(boundary)
        
        # Add end boundary
        if filtered[-1]["timestamp"] < video_duration:
            filtered.append({
                "timestamp": video_duration,
                "reasons": ["video_end"],
                "confidence": 1.0,
                "sources": ["system"]
            })
        
        return sorted(filtered, key=lambda x: x["timestamp"])
    
    def _create_segments(
        self,
        boundaries: List[Dict[str, Any]],
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any]
    ) -> List[VideoSegment]:
        """Create VideoSegment objects from boundaries."""
        segments = []
        
        for i in range(len(boundaries) - 1):
            start_time = boundaries[i]["timestamp"]
            end_time = boundaries[i + 1]["timestamp"]
            
            # Determine segment type
            segment_type = self._classify_segment(
                start_time, end_time, gemini_analysis, whisper_transcript
            )
            
            # Extract features
            features = self._extract_segment_features(
                start_time, end_time, gemini_analysis, whisper_transcript
            )
            
            segment = VideoSegment(
                start_time=start_time,
                end_time=end_time,
                segment_type=segment_type,
                primary_pattern=features.get("primary_pattern"),
                key_features=features.get("key_features", []),
                transcript_text=features.get("transcript_text"),
                visual_changes=features.get("visual_changes", [])
            )
            
            segments.append(segment)
        
        return segments
    
    def _classify_segment(
        self,
        start_time: float,
        end_time: float,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any]
    ) -> str:
        """Classify segment type based on content."""
        # Get transcript text for segment
        text = self._get_transcript_text(start_time, end_time, whisper_transcript)
        
        # Reason: Simple keyword-based classification
        text_lower = text.lower()
        if any(word in text_lower for word in ["explain", "show", "teach", "understand"]):
            return "explanation"
        elif any(word in text_lower for word in ["setup", "looking for", "waiting"]):
            return "setup"
        elif any(word in text_lower for word in ["enter", "buy", "sell", "execute"]):
            return "execution"
        elif any(word in text_lower for word in ["review", "result", "outcome", "happened"]):
            return "review"
        else:
            return "analysis"
    
    def _extract_segment_features(
        self,
        start_time: float,
        end_time: float,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract features for a segment."""
        features = {
            "transcript_text": self._get_transcript_text(start_time, end_time, whisper_transcript),
            "key_features": [],
            "visual_changes": [],
            "primary_pattern": None
        }
        
        # Extract patterns in this time range
        patterns = gemini_analysis.get("patterns", [])
        for pattern in patterns:
            if "timestamp" in pattern:
                ts = self._parse_timestamp(pattern["timestamp"])
                if start_time <= ts <= end_time:
                    features["key_features"].append(pattern.get("description", ""))
                    if features["primary_pattern"] is None:
                        features["primary_pattern"] = pattern.get("type", "unknown")
        
        return features
    
    def _get_transcript_text(
        self,
        start_time: float,
        end_time: float,
        whisper_transcript: Dict[str, Any]
    ) -> str:
        """Get transcript text for time range."""
        segments = whisper_transcript.get("segments", [])
        texts = []
        
        for seg in segments:
            seg_start = seg.get("start", 0)
            seg_end = seg.get("end", 0)
            
            # Reason: Include segments that overlap with time range
            if seg_start <= end_time and seg_end >= start_time:
                texts.append(seg.get("text", ""))
        
        return " ".join(texts)
    
    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse timestamp string to seconds."""
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
        
        # Handle HH:MM:SS or MM:SS formats
        parts = timestamp.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        else:
            return 0.0
