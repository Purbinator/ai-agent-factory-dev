"""Gemini 1.5 Pro video processor for dense multimodal analysis."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class VideoFrame:
    """Represents an extracted video frame."""
    timestamp: str  # HH:MM:SS format
    timestamp_seconds: float
    frame_number: int


@dataclass
class OrderflowPattern:
    """Represents an identified orderflow pattern."""
    pattern_type: str
    timestamp: str
    description: str
    confidence: float
    visual_markers: List[str]
    context: str


class GeminiVideoProcessor:
    """
    Process videos using Gemini 1.5 Pro for dense multimodal understanding.
    
    Analyzes trading/orderflow videos at 1 FPS to extract:
    - Visual orderflow dynamics
    - Pattern signatures
    - Cross-modal validation points
    """
    
    def __init__(self, gemini_client: genai.GenerativeModel, settings):
        """
        Initialize video processor.
        
        Args:
            gemini_client: Configured Gemini model client
            settings: Application settings
        """
        self.client = gemini_client
        self.settings = settings
        self.processing_results = {}
    
    async def process_video(
        self, 
        video_path: Path, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process video file with Gemini 1.5 Pro.
        
        Args:
            video_path: Path to video file
            prompt: Optional custom prompt (uses default if not provided)
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting Gemini video analysis: {video_path}")
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Upload video to Gemini
        logger.info("Uploading video to Gemini...")
        video_file = await self._upload_video(video_path)
        
        # Wait for video to be processed
        await self._wait_for_processing(video_file)
        
        # Generate analysis
        logger.info("Generating video analysis...")
        analysis = await self._generate_analysis(video_file, prompt)
        
        # Parse and structure results
        structured_results = self._structure_results(analysis)
        
        logger.info("Video analysis complete")
        return structured_results
    
    async def _upload_video(self, video_path: Path):
        """
        Upload video to Gemini.
        
        Args:
            video_path: Path to video file
        
        Returns:
            Uploaded file reference
        """
        # Reason: Run upload in thread pool since genai upload_file is synchronous
        loop = asyncio.get_event_loop()
        video_file = await loop.run_in_executor(
            None,
            genai.upload_file,
            str(video_path)
        )
        return video_file
    
    async def _wait_for_processing(self, video_file):
        """
        Wait for Gemini to process the uploaded video.
        
        Args:
            video_file: Uploaded file reference
        """
        # Reason: Poll until video is processed (required by Gemini API)
        while video_file.state.name == "PROCESSING":
            await asyncio.sleep(2)
            # Refresh file state
            loop = asyncio.get_event_loop()
            video_file = await loop.run_in_executor(
                None,
                genai.get_file,
                video_file.name
            )
        
        if video_file.state.name == "FAILED":
            raise RuntimeError("Video processing failed in Gemini")
    
    async def _generate_analysis(
        self, 
        video_file, 
        prompt: Optional[str] = None
    ) -> str:
        """
        Generate analysis using Gemini.
        
        Args:
            video_file: Uploaded video file
            prompt: Analysis prompt
        
        Returns:
            Raw analysis text
        """
        from ..prompts import GEMINI_VIDEO_ANALYSIS_PROMPT
        
        analysis_prompt = prompt or GEMINI_VIDEO_ANALYSIS_PROMPT
        
        # Reason: Run generation in thread pool since it's synchronous
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate_content(
                [video_file, analysis_prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=self.settings.gemini_temperature,
                    max_output_tokens=self.settings.gemini_max_output_tokens,
                )
            )
        )
        
        return response.text
    
    def _structure_results(self, raw_analysis: str) -> Dict[str, Any]:
        """
        Structure raw analysis into organized format.
        
        Args:
            raw_analysis: Raw text from Gemini
        
        Returns:
            Structured analysis dictionary
        """
        # Try to parse as JSON first
        try:
            # Reason: Gemini may return JSON in markdown code blocks
            if "```json" in raw_analysis:
                json_start = raw_analysis.find("```json") + 7
                json_end = raw_analysis.find("```", json_start)
                json_text = raw_analysis[json_start:json_end].strip()
                return json.loads(json_text)
            else:
                return json.loads(raw_analysis)
        except json.JSONDecodeError:
            logger.warning("Failed to parse as JSON, using text structure")
            return self._parse_text_analysis(raw_analysis)
    
    def _parse_text_analysis(self, text: str) -> Dict[str, Any]:
        """
        Parse text analysis into structured format.
        
        Args:
            text: Raw analysis text
        
        Returns:
            Structured dictionary
        """
        return {
            "raw_analysis": text,
            "patterns": self._extract_patterns(text),
            "timeline": self._extract_timeline(text),
            "visual_markers": self._extract_visual_markers(text),
            "cross_modal_points": self._extract_cross_modal_points(text),
        }
    
    def _extract_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract orderflow patterns from text."""
        patterns = []
        # Reason: Simple pattern extraction - can be enhanced with NLP
        lines = text.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["pattern", "imbalance", "order", "volume"]):
                patterns.append({
                    "description": line.strip(),
                    "type": "extracted",
                })
        return patterns
    
    def _extract_timeline(self, text: str) -> List[Dict[str, Any]]:
        """Extract timeline events from text."""
        import re
        timeline = []
        # Reason: Extract timestamp patterns (HH:MM:SS or MM:SS)
        timestamp_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
        matches = re.finditer(timestamp_pattern, text)
        for match in matches:
            timestamp = match.group(1)
            # Get context around timestamp
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            timeline.append({
                "timestamp": timestamp,
                "context": context,
            })
        return timeline
    
    def _extract_visual_markers(self, text: str) -> List[str]:
        """Extract visual marker references from text."""
        markers = []
        keywords = ["cursor", "highlight", "annotation", "arrow", "circle", "chart"]
        lines = text.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                markers.append(line.strip())
        return markers
    
    def _extract_cross_modal_points(self, text: str) -> List[Dict[str, Any]]:
        """Extract cross-modal validation points."""
        points = []
        keywords = ["confirm", "verify", "align", "match", "audio", "speech"]
        lines = text.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                points.append({
                    "description": line.strip(),
                    "validation_type": "cross_modal",
                })
        return points
    
    async def process_video_chunked(
        self,
        video_path: Path,
        chunk_duration_seconds: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Process long video in chunks.
        
        Args:
            video_path: Path to video file
            chunk_duration_seconds: Duration of each chunk
        
        Returns:
            List of analysis results per chunk
        """
        logger.info(f"Processing video in {chunk_duration_seconds}s chunks")
        
        # Reason: For videos longer than Gemini's context, process in chunks
        # This is a placeholder - actual implementation would split video file
        
        # For now, process entire video
        return [await self.process_video(video_path)]
