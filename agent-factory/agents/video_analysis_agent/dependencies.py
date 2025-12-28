"""Dependencies for Video Analysis Agent."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from openai import AsyncOpenAI
from settings import load_settings
from pathlib import Path


@dataclass
class AgentDependencies:
    """Dependencies injected into the agent context."""
    
    # Core dependencies
    gemini_client: Optional[genai.GenerativeModel] = None
    openai_client: Optional[AsyncOpenAI] = None
    settings: Optional[Any] = None
    
    # Processing state
    video_path: Optional[Path] = None
    current_stage: Optional[str] = None
    processing_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Extracted data storage
    gemini_analysis: Optional[Dict[str, Any]] = None
    whisper_transcript: Optional[Dict[str, Any]] = None
    semantic_chunks: Optional[List[Dict[str, Any]]] = None
    knowledge_graph: Optional[Dict[str, Any]] = None
    
    # Session context
    session_id: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    async def initialize(self):
        """
        Initialize external connections and clients.
        """
        if not self.settings:
            self.settings = load_settings()
        
        # Initialize Gemini client
        if not self.gemini_client:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.gemini_client = genai.GenerativeModel(self.settings.gemini_model)
        
        # Initialize OpenAI client (for Whisper API if enabled)
        if not self.openai_client and self.settings.whisper_use_api:
            self.openai_client = AsyncOpenAI(
                api_key=self.settings.whisper_api_key or self.settings.llm_api_key
            )
    
    async def cleanup(self):
        """
        Clean up external connections.
        """
        # Gemini and OpenAI clients don't require explicit cleanup
        self.gemini_client = None
        self.openai_client = None
    
    def set_video_path(self, video_path: str):
        """
        Set the video file path for processing.
        
        Args:
            video_path: Path to video file
        """
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
    
    def set_stage(self, stage: str):
        """
        Update the current processing stage.
        
        Args:
            stage: Stage name (gemini, whisper, chunking, knowledge_graph, system_prompt)
        """
        self.current_stage = stage
        self.processing_history.append({
            "stage": stage,
            "timestamp": self._get_timestamp()
        })
    
    def store_gemini_analysis(self, analysis: Dict[str, Any]):
        """
        Store Gemini video analysis results.
        
        Args:
            analysis: Analysis results from Gemini
        """
        self.gemini_analysis = analysis
    
    def store_whisper_transcript(self, transcript: Dict[str, Any]):
        """
        Store Whisper transcription results.
        
        Args:
            transcript: Transcription results from Whisper
        """
        self.whisper_transcript = transcript
    
    def store_semantic_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Store semantic chunk boundaries.
        
        Args:
            chunks: List of semantic chunks
        """
        self.semantic_chunks = chunks
    
    def store_knowledge_graph(self, kg: Dict[str, Any]):
        """
        Store assembled knowledge graph.
        
        Args:
            kg: Knowledge graph structure
        """
        self.knowledge_graph = kg
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Get all stored processing data.
        
        Returns:
            Dictionary with all processing results
        """
        return {
            "video_path": str(self.video_path) if self.video_path else None,
            "gemini_analysis": self.gemini_analysis,
            "whisper_transcript": self.whisper_transcript,
            "semantic_chunks": self.semantic_chunks,
            "knowledge_graph": self.knowledge_graph,
            "processing_history": self.processing_history,
        }
    
    def is_stage_complete(self, stage: str) -> bool:
        """
        Check if a processing stage is complete.
        
        Args:
            stage: Stage name to check
        
        Returns:
            True if stage has been completed
        """
        stage_data_map = {
            "gemini": self.gemini_analysis,
            "whisper": self.whisper_transcript,
            "chunking": self.semantic_chunks,
            "knowledge_graph": self.knowledge_graph,
        }
        
        return stage_data_map.get(stage) is not None
    
    def get_missing_stages(self) -> List[str]:
        """
        Get list of incomplete processing stages.
        
        Returns:
            List of stage names that haven't been completed
        """
        stages = ["gemini", "whisper", "chunking", "knowledge_graph"]
        return [stage for stage in stages if not self.is_stage_complete(stage)]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def set_user_preference(self, key: str, value: Any):
        """
        Set a user preference for the session.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value
