"""Knowledge graph assembly for video analysis results."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TimelineEvent:
    """Represents an event in the video timeline."""
    timestamp: float
    timestamp_str: str
    event_type: str
    description: str
    visual_data: Optional[Dict[str, Any]] = None
    audio_data: Optional[Dict[str, Any]] = None
    confidence: float = 1.0


@dataclass
class OrderflowRule:
    """Represents a trading rule extracted from video."""
    rule_id: str
    description: str
    pattern_name: str
    entry_conditions: List[str] = field(default_factory=list)
    exit_conditions: List[str] = field(default_factory=list)
    context_requirements: List[str] = field(default_factory=list)
    success_rate: Optional[float] = None
    occurrences: int = 0
    confidence: float = 0.0
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PatternSignature:
    """Represents a visual + audio pattern signature."""
    pattern_id: str
    pattern_name: str
    visual_characteristics: List[str] = field(default_factory=list)
    audio_confirmations: List[str] = field(default_factory=list)
    occurrence_count: int = 0
    reliability: float = 0.0
    timestamps: List[str] = field(default_factory=list)


@dataclass
class ConfidenceMatrix:
    """Confidence scoring rules for pattern recognition."""
    pattern_only: float = 0.65
    pattern_with_audio: float = 0.95
    multiple_occurrences_bonus: float = 0.05
    context_match_bonus: float = 0.10
    max_confidence: float = 0.99


class KnowledgeGraphBuilder:
    """
    Assemble knowledge graph from video analysis results.
    
    Synthesizes:
    - Gemini video analysis
    - Whisper transcription
    - Semantic chunks
    
    Into unified knowledge structure.
    """
    
    def __init__(self, settings):
        """
        Initialize knowledge graph builder.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.min_occurrences = settings.kg_min_pattern_occurrences
        self.confidence_threshold = settings.kg_confidence_threshold
    
    def build_knowledge_graph(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any],
        semantic_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build comprehensive knowledge graph.
        
        Args:
            gemini_analysis: Results from Gemini video processor
            whisper_transcript: Results from Whisper transcriber
            semantic_chunks: Results from semantic chunker
        
        Returns:
            Knowledge graph dictionary with 4 layers
        """
        logger.info("Building knowledge graph...")
        
        # Layer 1: Complete Timeline
        timeline = self._build_timeline(gemini_analysis, whisper_transcript, semantic_chunks)
        
        # Layer 2: Orderflow Rules
        rules = self._extract_rules(gemini_analysis, whisper_transcript, semantic_chunks)
        
        # Layer 3: Pattern Signatures
        signatures = self._build_pattern_signatures(gemini_analysis, whisper_transcript)
        
        # Layer 4: Confidence Matrix
        confidence_matrix = self._build_confidence_matrix(rules, signatures)
        
        knowledge_graph = {
            "timeline": [self._event_to_dict(e) for e in timeline],
            "orderflow_rules": [self._rule_to_dict(r) for r in rules],
            "pattern_signatures": [self._signature_to_dict(s) for s in signatures],
            "confidence_matrix": confidence_matrix,
            "metadata": {
                "total_events": len(timeline),
                "total_rules": len(rules),
                "total_patterns": len(signatures),
            }
        }
        
        logger.info(f"Knowledge graph built: {len(timeline)} events, {len(rules)} rules, {len(signatures)} patterns")
        return knowledge_graph
    
    def _build_timeline(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any],
        semantic_chunks: List[Dict[str, Any]]
    ) -> List[TimelineEvent]:
        """Build complete chronological timeline."""
        events = []
        
        # Add visual events from Gemini
        for pattern in gemini_analysis.get("patterns", []):
            if "timestamp" in pattern:
                timestamp = self._parse_timestamp(pattern["timestamp"])
                events.append(TimelineEvent(
                    timestamp=timestamp,
                    timestamp_str=pattern["timestamp"],
                    event_type="visual_pattern",
                    description=pattern.get("description", ""),
                    visual_data=pattern,
                    confidence=0.8
                ))
        
        # Add timeline events from Gemini
        for event in gemini_analysis.get("timeline", []):
            if "timestamp" in event:
                timestamp = self._parse_timestamp(event["timestamp"])
                events.append(TimelineEvent(
                    timestamp=timestamp,
                    timestamp_str=event["timestamp"],
                    event_type="visual_event",
                    description=event.get("context", ""),
                    visual_data=event,
                    confidence=0.7
                ))
        
        # Add audio events from Whisper
        for trigger in whisper_transcript.get("action_triggers", []):
            events.append(TimelineEvent(
                timestamp=trigger["start"],
                timestamp_str=self._seconds_to_timestamp(trigger["start"]),
                event_type="action_trigger",
                description=f"Trigger: {trigger['trigger']} - {trigger['text']}",
                audio_data=trigger,
                confidence=0.9
            ))
        
        for intent in whisper_transcript.get("trader_intent", []):
            events.append(TimelineEvent(
                timestamp=intent["start"],
                timestamp_str=self._seconds_to_timestamp(intent["start"]),
                event_type="trader_intent",
                description=intent["text"],
                audio_data=intent,
                confidence=0.75
            ))
        
        # Add segment boundaries
        for chunk in semantic_chunks:
            events.append(TimelineEvent(
                timestamp=chunk.get("start_time", 0),
                timestamp_str=chunk.get("timestamp_range", "").split(" - ")[0],
                event_type="segment_boundary",
                description=f"Segment: {chunk.get('segment_type', 'unknown')}",
                visual_data=chunk,
                confidence=1.0
            ))
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        
        # Merge nearby events (within 2 seconds)
        merged_events = self._merge_timeline_events(events)
        
        return merged_events
    
    def _merge_timeline_events(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        """Merge events that occur within 2 seconds of each other."""
        if not events:
            return []
        
        merged = []
        current_cluster = [events[0]]
        
        for i in range(1, len(events)):
            # Reason: Group events within 2 seconds as they're likely related
            if events[i].timestamp - current_cluster[0].timestamp <= 2.0:
                current_cluster.append(events[i])
            else:
                # Merge cluster and start new one
                merged.append(self._merge_event_cluster(current_cluster))
                current_cluster = [events[i]]
        
        # Merge final cluster
        if current_cluster:
            merged.append(self._merge_event_cluster(current_cluster))
        
        return merged
    
    def _merge_event_cluster(self, cluster: List[TimelineEvent]) -> TimelineEvent:
        """Merge a cluster of related events."""
        if len(cluster) == 1:
            return cluster[0]
        
        # Combine descriptions
        descriptions = [e.description for e in cluster]
        combined_desc = " | ".join(descriptions)
        
        # Use highest confidence
        max_confidence = max(e.confidence for e in cluster)
        
        # Combine data
        visual_data = {}
        audio_data = {}
        for e in cluster:
            if e.visual_data:
                visual_data.update(e.visual_data)
            if e.audio_data:
                audio_data.update(e.audio_data)
        
        return TimelineEvent(
            timestamp=cluster[0].timestamp,
            timestamp_str=cluster[0].timestamp_str,
            event_type="merged_event",
            description=combined_desc,
            visual_data=visual_data if visual_data else None,
            audio_data=audio_data if audio_data else None,
            confidence=max_confidence
        )
    
    def _extract_rules(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any],
        semantic_chunks: List[Dict[str, Any]]
    ) -> List[OrderflowRule]:
        """Extract trading rules from analysis."""
        rules = []
        rule_patterns = defaultdict(list)
        
        # Extract rules from visual patterns
        for pattern in gemini_analysis.get("patterns", []):
            pattern_type = pattern.get("type", "unknown")
            pattern_desc = pattern.get("description", "")
            
            rule_patterns[pattern_type].append({
                "source": "visual",
                "description": pattern_desc,
                "timestamp": pattern.get("timestamp", ""),
                "confidence": pattern.get("confidence", 0.7)
            })
        
        # Extract rules from trader intent
        for intent in whisper_transcript.get("trader_intent", []):
            # Reason: Intent statements often contain rule descriptions
            text = intent["text"]
            rule_patterns["trader_statement"].append({
                "source": "audio",
                "description": text,
                "timestamp": self._seconds_to_timestamp(intent["start"]),
                "confidence": 0.8
            })
        
        # Build rules from patterns
        rule_id = 1
        for pattern_name, occurrences in rule_patterns.items():
            if len(occurrences) >= self.min_occurrences:
                # Combine descriptions
                descriptions = [occ["description"] for occ in occurrences]
                combined_desc = descriptions[0] if descriptions else "No description"
                
                # Calculate confidence
                confidence = sum(occ["confidence"] for occ in occurrences) / len(occurrences)
                
                rule = OrderflowRule(
                    rule_id=f"RULE_{rule_id:03d}",
                    description=combined_desc,
                    pattern_name=pattern_name,
                    occurrences=len(occurrences),
                    confidence=confidence,
                    examples=[{
                        "timestamp": occ["timestamp"],
                        "description": occ["description"]
                    } for occ in occurrences[:3]]  # Keep top 3 examples
                )
                
                rules.append(rule)
                rule_id += 1
        
        # Filter by confidence threshold
        rules = [r for r in rules if r.confidence >= self.confidence_threshold]
        
        return rules
    
    def _build_pattern_signatures(
        self,
        gemini_analysis: Dict[str, Any],
        whisper_transcript: Dict[str, Any]
    ) -> List[PatternSignature]:
        """Build pattern signatures with visual + audio characteristics."""
        signatures = []
        pattern_data = defaultdict(lambda: {
            "visual": [],
            "audio": [],
            "timestamps": []
        })
        
        # Collect visual characteristics
        for pattern in gemini_analysis.get("patterns", []):
            pattern_type = pattern.get("type", "unknown")
            pattern_data[pattern_type]["visual"].append(pattern.get("description", ""))
            pattern_data[pattern_type]["timestamps"].append(pattern.get("timestamp", ""))
        
        # Collect visual markers
        for marker in gemini_analysis.get("visual_markers", []):
            pattern_data["visual_marker"]["visual"].append(marker)
        
        # Collect audio confirmations
        for trigger in whisper_transcript.get("action_triggers", []):
            pattern_data["action_pattern"]["audio"].append(trigger["trigger"])
            pattern_data["action_pattern"]["timestamps"].append(
                self._seconds_to_timestamp(trigger["start"])
            )
        
        # Build signatures
        pattern_id = 1
        for pattern_name, data in pattern_data.items():
            occurrence_count = max(len(data["visual"]), len(data["audio"]))
            
            if occurrence_count >= self.min_occurrences:
                signature = PatternSignature(
                    pattern_id=f"PAT_{pattern_id:03d}",
                    pattern_name=pattern_name,
                    visual_characteristics=list(set(data["visual"])),
                    audio_confirmations=list(set(data["audio"])),
                    occurrence_count=occurrence_count,
                    reliability=min(1.0, occurrence_count / 10.0),
                    timestamps=data["timestamps"][:5]  # Keep top 5
                )
                signatures.append(signature)
                pattern_id += 1
        
        return signatures
    
    def _build_confidence_matrix(
        self,
        rules: List[OrderflowRule],
        signatures: List[PatternSignature]
    ) -> Dict[str, Any]:
        """Build confidence scoring matrix."""
        matrix = ConfidenceMatrix()
        
        # Calculate average confidence across rules
        if rules:
            avg_rule_confidence = sum(r.confidence for r in rules) / len(rules)
        else:
            avg_rule_confidence = 0.5
        
        # Calculate average reliability across patterns
        if signatures:
            avg_pattern_reliability = sum(s.reliability for s in signatures) / len(signatures)
        else:
            avg_pattern_reliability = 0.5
        
        return {
            "pattern_only": matrix.pattern_only,
            "pattern_with_audio": matrix.pattern_with_audio,
            "multiple_occurrences_bonus": matrix.multiple_occurrences_bonus,
            "context_match_bonus": matrix.context_match_bonus,
            "max_confidence": matrix.max_confidence,
            "average_rule_confidence": round(avg_rule_confidence, 3),
            "average_pattern_reliability": round(avg_pattern_reliability, 3),
            "scoring_examples": [
                {
                    "scenario": "Pattern detected with audio confirmation",
                    "score": matrix.pattern_with_audio
                },
                {
                    "scenario": "Pattern detected without audio",
                    "score": matrix.pattern_only
                },
                {
                    "scenario": "Pattern + audio + 3+ occurrences",
                    "score": min(matrix.max_confidence, matrix.pattern_with_audio + 2 * matrix.multiple_occurrences_bonus)
                }
            ]
        }
    
    def _event_to_dict(self, event: TimelineEvent) -> Dict[str, Any]:
        """Convert TimelineEvent to dictionary."""
        return {
            "timestamp": event.timestamp,
            "timestamp_str": event.timestamp_str,
            "event_type": event.event_type,
            "description": event.description,
            "visual_data": event.visual_data,
            "audio_data": event.audio_data,
            "confidence": event.confidence
        }
    
    def _rule_to_dict(self, rule: OrderflowRule) -> Dict[str, Any]:
        """Convert OrderflowRule to dictionary."""
        return {
            "rule_id": rule.rule_id,
            "description": rule.description,
            "pattern_name": rule.pattern_name,
            "entry_conditions": rule.entry_conditions,
            "exit_conditions": rule.exit_conditions,
            "context_requirements": rule.context_requirements,
            "success_rate": rule.success_rate,
            "occurrences": rule.occurrences,
            "confidence": round(rule.confidence, 3),
            "examples": rule.examples
        }
    
    def _signature_to_dict(self, signature: PatternSignature) -> Dict[str, Any]:
        """Convert PatternSignature to dictionary."""
        return {
            "pattern_id": signature.pattern_id,
            "pattern_name": signature.pattern_name,
            "visual_characteristics": signature.visual_characteristics,
            "audio_confirmations": signature.audio_confirmations,
            "occurrence_count": signature.occurrence_count,
            "reliability": round(signature.reliability, 3),
            "timestamps": signature.timestamps
        }
    
    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse timestamp string to seconds."""
        if isinstance(timestamp, (int, float)):
            return float(timestamp)
        
        parts = timestamp.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        return 0.0
    
    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
