#!/usr/bin/env python3
"""
Example: Orderflow Trading Video Analysis

This script demonstrates how to use the Video Analysis Agent
to extract orderflow patterns with success rates from trading videos.
"""

import asyncio
import json
from pathlib import Path

# Import agent components
from dependencies import AgentDependencies
from ingestion import (
    GeminiVideoProcessor,
    WhisperTranscriber,
    SemanticVideoChunker,
    KnowledgeGraphBuilder,
    SystemPromptGenerator
)


async def analyze_orderflow_video(video_path: str):
    """
    Analyze an orderflow trading video and extract patterns with success rates.
    
    Args:
        video_path: Path to the trading video file
    """
    print(f"🎯 Analyzing Orderflow Trading Video: {video_path}")
    print("=" * 60)
    
    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()
    deps.set_video_path(video_path)
    
    try:
        # Stage 1: Gemini Video Analysis (Enhanced for Orderflow)
        print("\n📹 Stage 1: Gemini Video Analysis...")
        processor = GeminiVideoProcessor(deps.gemini_client, deps.settings)
        gemini_analysis = await processor.process_video(Path(video_path))
        deps.store_gemini_analysis(gemini_analysis)
        
        print(f"   ✓ Extracted {len(gemini_analysis.get('patterns', []))} patterns")
        
        # Show DOM data if extracted
        for pattern in gemini_analysis.get('patterns', [])[:3]:
            if 'dom_ratio_before' in pattern:
                print(f"   → Pattern: {pattern['type']}, DOM: {pattern['dom_ratio_before']}")
        
        # Stage 2: Whisper Transcription
        print("\n🎤 Stage 2: Whisper Transcription...")
        transcriber = WhisperTranscriber(deps.openai_client, deps.settings)
        transcript = await transcriber.transcribe_video(Path(video_path))
        deps.store_whisper_transcript(transcript)
        
        print(f"   ✓ Transcribed {len(transcript.get('segments', []))} segments")
        print(f"   ✓ Found {len(transcript.get('action_triggers', []))} action triggers")
        
        # Stage 3: Semantic Chunking
        print("\n🔗 Stage 3: Semantic Chunking...")
        chunker = SemanticVideoChunker(deps.settings)
        chunks = chunker.chunk_video(gemini_analysis, transcript)
        
        chunks_dict = [
            {
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "segment_type": seg.segment_type,
                "timestamp_range": seg.timestamp_range
            }
            for seg in chunks
        ]
        deps.store_semantic_chunks(chunks_dict)
        
        print(f"   ✓ Created {len(chunks)} semantic segments")
        
        # Stage 4: Knowledge Graph Assembly (With Success Rates)
        print("\n🧠 Stage 4: Knowledge Graph Assembly...")
        kg_builder = KnowledgeGraphBuilder(deps.settings)
        knowledge_graph = kg_builder.build_knowledge_graph(
            gemini_analysis,
            transcript,
            chunks_dict
        )
        deps.store_knowledge_graph(knowledge_graph)
        
        metadata = knowledge_graph["metadata"]
        print(f"   ✓ Timeline events: {metadata['total_events']}")
        print(f"   ✓ Orderflow rules: {metadata['total_rules']}")
        print(f"   ✓ Pattern signatures: {metadata['total_patterns']}")
        
        # Show rules with success rates
        print("\n📊 Orderflow Rules with Success Rates:")
        print("-" * 60)
        
        for rule in knowledge_graph["orderflow_rules"]:
            print(f"\n{rule['rule_id']}: {rule['pattern_name'].upper()}")
            print(f"  Description: {rule['description'][:60]}...")
            print(f"  Occurrences: {rule['occurrences']}")
            print(f"  Confidence: {rule['confidence']:.2f}")
            
            if rule['success_rate'] is not None:
                success_pct = rule['success_rate'] * 100
                print(f"  ✅ Success Rate: {success_pct:.1f}%")
                
                if 'outcome_count' in rule:
                    print(f"  📈 Outcomes Tracked: {rule['outcome_count']}")
                    
                    # Show outcome details
                    if 'outcomes' in rule:
                        successful = sum(1 for o in rule['outcomes'] if o.get('success'))
                        failed = len(rule['outcomes']) - successful
                        print(f"     → Successful: {successful}, Failed: {failed}")
            else:
                print(f"  ⚠️  Success Rate: Not tracked (no outcomes in video)")
        
        # Show pattern signatures
        print("\n\n🎯 Pattern Signatures:")
        print("-" * 60)
        
        for pattern in knowledge_graph["pattern_signatures"][:5]:
            print(f"\n{pattern['pattern_id']}: {pattern['pattern_name']}")
            print(f"  Occurrences: {pattern['occurrence_count']}")
            print(f"  Reliability: {pattern['reliability']:.2f}")
            
            if pattern['visual_characteristics']:
                print(f"  Visual: {pattern['visual_characteristics'][0][:50]}...")
            
            if pattern['audio_confirmations']:
                print(f"  Audio: {', '.join(pattern['audio_confirmations'][:3])}")
        
        # Stage 5: System Prompt Generation
        print("\n\n📝 Stage 5: System Prompt Generation...")
        generator = SystemPromptGenerator(deps.settings)
        output_path = generator.generate_system_prompt(
            knowledge_graph,
            video_path,
            "orderflow_system_prompt.txt"
        )
        
        print(f"   ✓ System prompt saved to: {output_path}")
        print(f"   ✓ JSON knowledge graph: {output_path.with_suffix('.json')}")
        
        # Generate summary report
        summary = generator.generate_summary_report(knowledge_graph)
        print("\n" + "=" * 60)
        print(summary)
        print("=" * 60)
        
        # Show confidence matrix
        print("\n\n🎲 Confidence Scoring Matrix:")
        print("-" * 60)
        cm = knowledge_graph["confidence_matrix"]
        print(f"Pattern only: {cm['pattern_only']:.2f}")
        print(f"Pattern + audio: {cm['pattern_with_audio']:.2f}")
        print(f"Multiple occurrences bonus: +{cm['multiple_occurrences_bonus']:.2f}")
        print(f"Context match bonus: +{cm['context_match_bonus']:.2f}")
        
        print("\n\n✅ Analysis Complete!")
        print(f"\nNext Steps:")
        print(f"  1. Review: cat {output_path}")
        print(f"  2. Use in trading system: Load system_prompt.txt as knowledge base")
        print(f"  3. Programmatic access: Load system_prompt.json")
        
    finally:
        await deps.cleanup()


async def compare_patterns(video_path1: str, video_path2: str):
    """
    Compare patterns from two different videos.
    
    Args:
        video_path1: First trading video
        video_path2: Second trading video
    """
    print("🔄 Comparing Patterns Across Videos...")
    
    # Analyze both videos
    # (Implementation would process both and compare results)
    pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_orderflow_analysis.py <video_path>")
        print("\nExample:")
        print("  python example_orderflow_analysis.py trading_session.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Run analysis
    asyncio.run(analyze_orderflow_video(video_path))
