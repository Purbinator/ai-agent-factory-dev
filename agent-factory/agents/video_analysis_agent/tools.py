"""Tools for Video Analysis Agent."""

from typing import Dict, Any, Optional
from pydantic_ai import RunContext
from pathlib import Path
import logging

from dependencies import AgentDependencies
from ingestion import (
    GeminiVideoProcessor,
    WhisperTranscriber,
    SemanticVideoChunker,
    KnowledgeGraphBuilder,
    SystemPromptGenerator
)

logger = logging.getLogger(__name__)


async def process_video_with_gemini(
    ctx: RunContext[AgentDependencies],
    video_path: str,
    custom_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process video using Gemini 1.5 Pro for dense multimodal analysis.
    
    Args:
        ctx: Agent runtime context
        video_path: Path to video file
        custom_prompt: Optional custom analysis prompt
    
    Returns:
        Dictionary with Gemini analysis results
    """
    try:
        deps = ctx.deps
        
        # Ensure dependencies are initialized
        if not deps.gemini_client:
            await deps.initialize()
        
        # Set video path
        deps.set_video_path(video_path)
        deps.set_stage("gemini")
        
        # Create processor
        processor = GeminiVideoProcessor(deps.gemini_client, deps.settings)
        
        # Process video
        analysis = await processor.process_video(Path(video_path), custom_prompt)
        
        # Store results
        deps.store_gemini_analysis(analysis)
        
        logger.info("Gemini video analysis complete")
        return {
            "status": "success",
            "analysis": analysis,
            "stage": "gemini_complete"
        }
        
    except Exception as e:
        logger.error(f"Gemini processing failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "stage": "gemini_failed"
        }


async def transcribe_with_whisper(
    ctx: RunContext[AgentDependencies],
    video_path: Optional[str] = None,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe video audio using Whisper with word-level timestamps.
    
    Args:
        ctx: Agent runtime context
        video_path: Path to video file (uses stored path if None)
        language: Language code (uses settings default if None)
    
    Returns:
        Dictionary with transcription results
    """
    try:
        deps = ctx.deps
        
        # Ensure dependencies are initialized
        if not deps.openai_client and deps.settings.whisper_use_api:
            await deps.initialize()
        
        # Use stored video path if not provided
        if video_path:
            deps.set_video_path(video_path)
        
        if not deps.video_path:
            return {
                "status": "error",
                "error": "No video path provided or stored",
                "stage": "whisper_failed"
            }
        
        deps.set_stage("whisper")
        
        # Create transcriber
        transcriber = WhisperTranscriber(deps.openai_client, deps.settings)
        
        # Transcribe
        transcript = await transcriber.transcribe_video(deps.video_path, language)
        
        # Store results
        deps.store_whisper_transcript(transcript)
        
        logger.info("Whisper transcription complete")
        return {
            "status": "success",
            "transcript": transcript,
            "stage": "whisper_complete"
        }
        
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "stage": "whisper_failed"
        }


async def chunk_video_semantically(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    Chunk video into semantic segments based on orderflow state changes.
    
    Requires Gemini analysis and Whisper transcript to be completed first.
    
    Args:
        ctx: Agent runtime context
    
    Returns:
        Dictionary with semantic chunks
    """
    try:
        deps = ctx.deps
        
        # Check prerequisites
        if not deps.gemini_analysis:
            return {
                "status": "error",
                "error": "Gemini analysis not complete. Run process_video_with_gemini first.",
                "stage": "chunking_failed"
            }
        
        if not deps.whisper_transcript:
            return {
                "status": "error",
                "error": "Whisper transcript not complete. Run transcribe_with_whisper first.",
                "stage": "chunking_failed"
            }
        
        deps.set_stage("chunking")
        
        # Create chunker
        chunker = SemanticVideoChunker(deps.settings)
        
        # Chunk video
        segments = chunker.chunk_video(
            deps.gemini_analysis,
            deps.whisper_transcript
        )
        
        # Convert segments to dicts
        chunks_dict = [
            {
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "duration": seg.duration,
                "segment_type": seg.segment_type,
                "primary_pattern": seg.primary_pattern,
                "key_features": seg.key_features,
                "transcript_text": seg.transcript_text,
                "visual_changes": seg.visual_changes,
                "timestamp_range": seg.timestamp_range
            }
            for seg in segments
        ]
        
        # Store results
        deps.store_semantic_chunks(chunks_dict)
        
        logger.info(f"Semantic chunking complete: {len(segments)} segments")
        return {
            "status": "success",
            "chunks": chunks_dict,
            "num_segments": len(segments),
            "stage": "chunking_complete"
        }
        
    except Exception as e:
        logger.error(f"Semantic chunking failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "stage": "chunking_failed"
        }


async def build_knowledge_graph(
    ctx: RunContext[AgentDependencies]
) -> Dict[str, Any]:
    """
    Build knowledge graph from all analysis results.
    
    Requires all previous stages to be completed.
    
    Args:
        ctx: Agent runtime context
    
    Returns:
        Dictionary with knowledge graph
    """
    try:
        deps = ctx.deps
        
        # Check prerequisites
        missing_stages = deps.get_missing_stages()
        if missing_stages:
            return {
                "status": "error",
                "error": f"Missing stages: {', '.join(missing_stages)}. Complete them first.",
                "missing_stages": missing_stages,
                "stage": "knowledge_graph_failed"
            }
        
        deps.set_stage("knowledge_graph")
        
        # Create builder
        builder = KnowledgeGraphBuilder(deps.settings)
        
        # Build knowledge graph
        kg = builder.build_knowledge_graph(
            deps.gemini_analysis,
            deps.whisper_transcript,
            deps.semantic_chunks
        )
        
        # Store results
        deps.store_knowledge_graph(kg)
        
        logger.info("Knowledge graph built successfully")
        return {
            "status": "success",
            "knowledge_graph": kg,
            "metadata": kg.get("metadata", {}),
            "stage": "knowledge_graph_complete"
        }
        
    except Exception as e:
        logger.error(f"Knowledge graph building failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "stage": "knowledge_graph_failed"
        }


async def generate_system_prompt(
    ctx: RunContext[AgentDependencies],
    output_filename: str = "system_prompt.txt"
) -> Dict[str, Any]:
    """
    Generate system prompt from knowledge graph.
    
    Requires knowledge graph to be built first.
    
    Args:
        ctx: Agent runtime context
        output_filename: Output filename
    
    Returns:
        Dictionary with generation results and path to output file
    """
    try:
        deps = ctx.deps
        
        # Check prerequisites
        if not deps.knowledge_graph:
            return {
                "status": "error",
                "error": "Knowledge graph not built. Run build_knowledge_graph first.",
                "stage": "prompt_generation_failed"
            }
        
        deps.set_stage("system_prompt")
        
        # Create generator
        generator = SystemPromptGenerator(deps.settings)
        
        # Generate prompt
        output_path = generator.generate_system_prompt(
            deps.knowledge_graph,
            str(deps.video_path),
            output_filename
        )
        
        # Generate summary report
        summary = generator.generate_summary_report(deps.knowledge_graph)
        
        logger.info(f"System prompt generated: {output_path}")
        return {
            "status": "success",
            "output_path": str(output_path),
            "summary": summary,
            "stage": "system_prompt_complete"
        }
        
    except Exception as e:
        logger.error(f"System prompt generation failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "stage": "prompt_generation_failed"
        }


async def run_full_pipeline(
    ctx: RunContext[AgentDependencies],
    video_path: str
) -> Dict[str, Any]:
    """
    Run the complete video analysis pipeline.
    
    Executes all stages in sequence:
    1. Gemini video analysis
    2. Whisper transcription
    3. Semantic chunking
    4. Knowledge graph assembly
    5. System prompt generation
    
    Args:
        ctx: Agent runtime context
        video_path: Path to video file
    
    Returns:
        Dictionary with complete pipeline results
    """
    results = {
        "pipeline": "full",
        "video_path": video_path,
        "stages": {}
    }
    
    try:
        # Stage 1: Gemini
        logger.info("Pipeline Stage 1: Gemini video analysis")
        gemini_result = await process_video_with_gemini(ctx, video_path)
        results["stages"]["gemini"] = gemini_result
        
        if gemini_result["status"] != "success":
            return results
        
        # Stage 2: Whisper
        logger.info("Pipeline Stage 2: Whisper transcription")
        whisper_result = await transcribe_with_whisper(ctx)
        results["stages"]["whisper"] = whisper_result
        
        if whisper_result["status"] != "success":
            return results
        
        # Stage 3: Chunking
        logger.info("Pipeline Stage 3: Semantic chunking")
        chunking_result = await chunk_video_semantically(ctx)
        results["stages"]["chunking"] = chunking_result
        
        if chunking_result["status"] != "success":
            return results
        
        # Stage 4: Knowledge Graph
        logger.info("Pipeline Stage 4: Knowledge graph assembly")
        kg_result = await build_knowledge_graph(ctx)
        results["stages"]["knowledge_graph"] = kg_result
        
        if kg_result["status"] != "success":
            return results
        
        # Stage 5: System Prompt
        logger.info("Pipeline Stage 5: System prompt generation")
        prompt_result = await generate_system_prompt(ctx)
        results["stages"]["system_prompt"] = prompt_result
        
        results["status"] = "success"
        results["message"] = "Full pipeline completed successfully"
        
        logger.info("Full pipeline complete")
        return results
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        results["status"] = "error"
        results["error"] = str(e)
        return results
