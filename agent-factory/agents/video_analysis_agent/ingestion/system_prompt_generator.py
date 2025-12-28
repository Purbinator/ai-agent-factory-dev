"""System prompt generator from knowledge graph."""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemPromptGenerator:
    """
    Generate production-ready system prompts from knowledge graph.
    
    Transforms structured knowledge into human-readable + machine-parseable
    prompt format for trading agents.
    """
    
    def __init__(self, settings):
        """
        Initialize system prompt generator.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.output_dir = Path(settings.output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_system_prompt(
        self,
        knowledge_graph: Dict[str, Any],
        video_path: str,
        output_filename: str = "system_prompt.txt"
    ) -> Path:
        """
        Generate system prompt from knowledge graph.
        
        Args:
            knowledge_graph: Assembled knowledge graph
            video_path: Source video path
            output_filename: Output filename
        
        Returns:
            Path to generated system prompt file
        """
        logger.info("Generating system prompt...")
        
        # Build prompt sections
        sections = []
        
        # Header
        sections.append(self._generate_header(video_path))
        
        # Overview
        sections.append(self._generate_overview(knowledge_graph))
        
        # Timeline Reference
        sections.append(self._generate_timeline_reference(knowledge_graph))
        
        # Core Rules
        sections.append(self._generate_core_rules(knowledge_graph))
        
        # Pattern Library
        sections.append(self._generate_pattern_library(knowledge_graph))
        
        # Decision Framework
        sections.append(self._generate_decision_framework(knowledge_graph))
        
        # Risk Management (if available)
        sections.append(self._generate_risk_management(knowledge_graph))
        
        # Combine sections
        full_prompt = "\n\n".join(sections)
        
        # Write to file
        output_path = self.output_dir / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_prompt)
        
        # Also save as JSON for machine parsing
        json_path = self.output_dir / output_filename.replace(".txt", ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(knowledge_graph, f, indent=2)
        
        logger.info(f"System prompt generated: {output_path}")
        return output_path
    
    def _generate_header(self, video_path: str) -> str:
        """Generate header section."""
        return f"""# Trading System Prompt
Generated from: {Path(video_path).name}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source: Video Analysis Agent - Gemini + Whisper

---"""
    
    def _generate_overview(self, kg: Dict[str, Any]) -> str:
        """Generate overview section."""
        metadata = kg.get("metadata", {})
        
        return f"""## OVERVIEW

This system prompt encodes trading knowledge extracted from {metadata.get('total_events', 0)} video events, 
identifying {metadata.get('total_rules', 0)} orderflow rules and {metadata.get('total_patterns', 0)} pattern signatures.

**Approach**: Orderflow-based trading using DOM imbalances, volume patterns, and price action.

**Key Principles**:
- Wait for confirmed orderflow signals before entry
- Use cross-modal validation (visual + audio confirmation)
- Manage risk according to pattern confidence scores
- Adapt to market context and conditions"""
    
    def _generate_timeline_reference(self, kg: Dict[str, Any]) -> str:
        """Generate timeline reference section."""
        timeline = kg.get("timeline", [])
        
        # Select key moments (high confidence events)
        key_moments = sorted(
            [e for e in timeline if e.get("confidence", 0) >= 0.8],
            key=lambda e: e.get("confidence", 0),
            reverse=True
        )[:10]
        
        lines = ["## TIMELINE REFERENCE", "", "Key moments from source video:"]
        
        for i, event in enumerate(key_moments, 1):
            timestamp = event.get("timestamp_str", "00:00:00")
            event_type = event.get("event_type", "unknown")
            description = event.get("description", "")[:100]
            confidence = event.get("confidence", 0)
            
            lines.append(f"{i}. [{timestamp}] ({event_type}, conf: {confidence:.2f})")
            lines.append(f"   {description}")
        
        return "\n".join(lines)
    
    def _generate_core_rules(self, kg: Dict[str, Any]) -> str:
        """Generate core rules section."""
        rules = kg.get("orderflow_rules", [])
        
        lines = ["## CORE TRADING RULES", ""]
        
        for rule in rules:
            rule_id = rule.get("rule_id", "")
            pattern_name = rule.get("pattern_name", "")
            description = rule.get("description", "")
            confidence = rule.get("confidence", 0)
            occurrences = rule.get("occurrences", 0)
            
            lines.append(f"### {rule_id}: {pattern_name.replace('_', ' ').title()}")
            lines.append(f"**Confidence**: {confidence:.2f} | **Occurrences**: {occurrences}")
            lines.append(f"**Description**: {description}")
            
            # Entry conditions
            entry_conditions = rule.get("entry_conditions", [])
            if entry_conditions:
                lines.append("**Entry Conditions**:")
                for cond in entry_conditions:
                    lines.append(f"  - {cond}")
            
            # Exit conditions
            exit_conditions = rule.get("exit_conditions", [])
            if exit_conditions:
                lines.append("**Exit Conditions**:")
                for cond in exit_conditions:
                    lines.append(f"  - {cond}")
            
            # Examples
            examples = rule.get("examples", [])
            if examples:
                lines.append("**Examples**:")
                for ex in examples[:2]:
                    timestamp = ex.get("timestamp", "")
                    lines.append(f"  - [{timestamp}] {ex.get('description', '')[:80]}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_pattern_library(self, kg: Dict[str, Any]) -> str:
        """Generate pattern library section."""
        patterns = kg.get("pattern_signatures", [])
        
        lines = ["## PATTERN LIBRARY", ""]
        
        for pattern in patterns:
            pattern_id = pattern.get("pattern_id", "")
            pattern_name = pattern.get("pattern_name", "")
            reliability = pattern.get("reliability", 0)
            occurrence_count = pattern.get("occurrence_count", 0)
            
            lines.append(f"### {pattern_id}: {pattern_name.replace('_', ' ').title()}")
            lines.append(f"**Reliability**: {reliability:.2f} | **Occurrences**: {occurrence_count}")
            
            # Visual characteristics
            visual = pattern.get("visual_characteristics", [])
            if visual:
                lines.append("**Visual Signatures**:")
                for char in visual[:5]:
                    lines.append(f"  - {char}")
            
            # Audio confirmations
            audio = pattern.get("audio_confirmations", [])
            if audio:
                lines.append("**Audio Confirmations**:")
                for conf in audio[:5]:
                    lines.append(f"  - \"{conf}\"")
            
            # Timestamps
            timestamps = pattern.get("timestamps", [])
            if timestamps:
                lines.append(f"**Observed at**: {', '.join(timestamps[:3])}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_decision_framework(self, kg: Dict[str, Any]) -> str:
        """Generate decision framework section."""
        confidence_matrix = kg.get("confidence_matrix", {})
        
        lines = ["## DECISION FRAMEWORK", ""]
        
        lines.append("### Pattern Recognition Confidence Scores")
        lines.append("")
        
        # Scoring rules
        pattern_only = confidence_matrix.get("pattern_only", 0.65)
        pattern_with_audio = confidence_matrix.get("pattern_with_audio", 0.95)
        multi_bonus = confidence_matrix.get("multiple_occurrences_bonus", 0.05)
        context_bonus = confidence_matrix.get("context_match_bonus", 0.10)
        
        lines.append(f"- **Pattern visual only**: {pattern_only:.2f}")
        lines.append(f"- **Pattern + audio confirmation**: {pattern_with_audio:.2f}")
        lines.append(f"- **Multiple occurrence bonus**: +{multi_bonus:.2f} per occurrence")
        lines.append(f"- **Context match bonus**: +{context_bonus:.2f}")
        lines.append("")
        
        # Examples
        lines.append("### Scoring Examples")
        for example in confidence_matrix.get("scoring_examples", []):
            scenario = example.get("scenario", "")
            score = example.get("score", 0)
            lines.append(f"- {scenario}: **{score:.2f}**")
        
        lines.append("")
        lines.append("### Decision Logic")
        lines.append("")
        lines.append("```")
        lines.append("IF pattern_confidence >= 0.95:")
        lines.append("    EXECUTE trade with full position size")
        lines.append("ELIF pattern_confidence >= 0.80:")
        lines.append("    EXECUTE trade with 50% position size")
        lines.append("ELIF pattern_confidence >= 0.65:")
        lines.append("    MONITOR for additional confirmation")
        lines.append("ELSE:")
        lines.append("    SKIP (insufficient confidence)")
        lines.append("```")
        
        return "\n".join(lines)
    
    def _generate_risk_management(self, kg: Dict[str, Any]) -> str:
        """Generate risk management section."""
        lines = ["## RISK MANAGEMENT", ""]
        
        # Extract risk-related rules
        rules = kg.get("orderflow_rules", [])
        risk_rules = [r for r in rules if any(
            keyword in r.get("description", "").lower() 
            for keyword in ["stop", "loss", "risk", "exit", "size"]
        )]
        
        if risk_rules:
            lines.append("### Risk Rules from Video")
            for rule in risk_rules[:5]:
                lines.append(f"- {rule.get('description', '')}")
            lines.append("")
        
        # General risk management
        lines.append("### General Risk Guidelines")
        lines.append("")
        lines.append("- Position size based on pattern confidence")
        lines.append("- Always use stop losses")
        lines.append("- Adjust risk per market volatility")
        lines.append("- Scale in/out based on confirmation strength")
        lines.append("- Maximum risk per trade: 1-2% of account")
        
        return "\n".join(lines)
    
    def generate_summary_report(self, knowledge_graph: Dict[str, Any]) -> str:
        """
        Generate summary report of extraction results.
        
        Args:
            knowledge_graph: Assembled knowledge graph
        
        Returns:
            Summary text
        """
        metadata = knowledge_graph.get("metadata", {})
        rules = knowledge_graph.get("orderflow_rules", [])
        patterns = knowledge_graph.get("pattern_signatures", [])
        timeline = knowledge_graph.get("timeline", [])
        
        report = f"""
# Video Analysis Summary Report

## Extraction Results
- Total Events: {metadata.get('total_events', 0)}
- Trading Rules: {metadata.get('total_rules', 0)}
- Pattern Signatures: {metadata.get('total_patterns', 0)}

## High Confidence Rules
"""
        
        high_conf_rules = [r for r in rules if r.get("confidence", 0) >= 0.8]
        for rule in high_conf_rules[:5]:
            report += f"\n- {rule.get('rule_id', '')}: {rule.get('pattern_name', '')} (conf: {rule.get('confidence', 0):.2f})\n"
        
        report += f"""
## Most Reliable Patterns
"""
        reliable_patterns = sorted(patterns, key=lambda p: p.get("reliability", 0), reverse=True)
        for pattern in reliable_patterns[:5]:
            report += f"\n- {pattern.get('pattern_id', '')}: {pattern.get('pattern_name', '')} (reliability: {pattern.get('reliability', 0):.2f})\n"
        
        return report
