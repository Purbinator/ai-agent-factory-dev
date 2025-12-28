#!/usr/bin/env python3
"""Command-line interface for Video Analysis Agent."""

import asyncio
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

from agent import get_video_analysis_agent
from dependencies import AgentDependencies
from settings import load_settings
from ingestion import (
    GeminiVideoProcessor,
    WhisperTranscriber,
    SemanticVideoChunker,
    KnowledgeGraphBuilder,
    SystemPromptGenerator
)

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_gemini_stage(video_path: Path, deps: AgentDependencies) -> dict:
    """Run Gemini video analysis stage."""
    console.print("\n[bold cyan]Phase 1: Gemini Video Analysis[/bold cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing video with Gemini 1.5 Pro...", total=None)
        
        processor = GeminiVideoProcessor(deps.gemini_client, deps.settings)
        analysis = await processor.process_video(video_path)
        
        progress.update(task, completed=True)
    
    deps.store_gemini_analysis(analysis)
    
    # Display summary
    console.print(f"✓ Extracted {len(analysis.get('patterns', []))} patterns")
    console.print(f"✓ Identified {len(analysis.get('timeline', []))} timeline events")
    
    return analysis


async def run_whisper_stage(video_path: Path, deps: AgentDependencies) -> dict:
    """Run Whisper transcription stage."""
    console.print("\n[bold cyan]Phase 2: Whisper Transcription[/bold cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing audio with Whisper...", total=None)
        
        transcriber = WhisperTranscriber(deps.openai_client, deps.settings)
        transcript = await transcriber.transcribe_video(video_path)
        
        progress.update(task, completed=True)
    
    deps.store_whisper_transcript(transcript)
    
    # Display summary
    console.print(f"✓ Transcribed {len(transcript.get('segments', []))} segments")
    console.print(f"✓ Duration: {transcript.get('duration', 0):.1f} seconds")
    console.print(f"✓ Found {len(transcript.get('action_triggers', []))} action triggers")
    
    return transcript


async def run_chunking_stage(deps: AgentDependencies) -> list:
    """Run semantic chunking stage."""
    console.print("\n[bold cyan]Phase 3: Semantic Chunking[/bold cyan]\n")
    
    if not deps.gemini_analysis or not deps.whisper_transcript:
        console.print("[red]Error: Gemini analysis and Whisper transcript required[/red]")
        return []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating semantic segments...", total=None)
        
        chunker = SemanticVideoChunker(deps.settings)
        segments = chunker.chunk_video(deps.gemini_analysis, deps.whisper_transcript)
        
        progress.update(task, completed=True)
    
    # Convert to dicts
    chunks_dict = [
        {
            "start_time": seg.start_time,
            "end_time": seg.end_time,
            "duration": seg.duration,
            "segment_type": seg.segment_type,
            "primary_pattern": seg.primary_pattern,
            "key_features": seg.key_features,
            "timestamp_range": seg.timestamp_range
        }
        for seg in segments
    ]
    
    deps.store_semantic_chunks(chunks_dict)
    
    # Display summary
    console.print(f"✓ Created {len(segments)} semantic segments")
    
    # Show segment types distribution
    segment_types = {}
    for seg in segments:
        seg_type = seg.segment_type
        segment_types[seg_type] = segment_types.get(seg_type, 0) + 1
    
    console.print("\nSegment Types:")
    for seg_type, count in segment_types.items():
        console.print(f"  - {seg_type}: {count}")
    
    return chunks_dict


async def run_knowledge_graph_stage(deps: AgentDependencies) -> dict:
    """Run knowledge graph assembly stage."""
    console.print("\n[bold cyan]Phase 4: Knowledge Graph Assembly[/bold cyan]\n")
    
    missing = deps.get_missing_stages()
    if missing:
        console.print(f"[red]Error: Missing stages: {', '.join(missing)}[/red]")
        return {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Building knowledge graph...", total=None)
        
        builder = KnowledgeGraphBuilder(deps.settings)
        kg = builder.build_knowledge_graph(
            deps.gemini_analysis,
            deps.whisper_transcript,
            deps.semantic_chunks
        )
        
        progress.update(task, completed=True)
    
    deps.store_knowledge_graph(kg)
    
    # Display summary
    metadata = kg.get("metadata", {})
    console.print(f"✓ Timeline events: {metadata.get('total_events', 0)}")
    console.print(f"✓ Orderflow rules: {metadata.get('total_rules', 0)}")
    console.print(f"✓ Pattern signatures: {metadata.get('total_patterns', 0)}")
    
    # Show top rules
    rules = kg.get("orderflow_rules", [])
    if rules:
        console.print("\n[bold]Top Rules:[/bold]")
        for rule in rules[:3]:
            console.print(f"  - {rule.get('rule_id', '')}: {rule.get('pattern_name', '')} (conf: {rule.get('confidence', 0):.2f})")
    
    return kg


async def run_system_prompt_stage(deps: AgentDependencies, output_filename: str) -> Path:
    """Run system prompt generation stage."""
    console.print("\n[bold cyan]Phase 5: System Prompt Generation[/bold cyan]\n")
    
    if not deps.knowledge_graph:
        console.print("[red]Error: Knowledge graph not built[/red]")
        return None
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating system prompt...", total=None)
        
        generator = SystemPromptGenerator(deps.settings)
        output_path = generator.generate_system_prompt(
            deps.knowledge_graph,
            str(deps.video_path),
            output_filename
        )
        
        progress.update(task, completed=True)
    
    console.print(f"✓ System prompt saved to: [green]{output_path}[/green]")
    
    # Display summary
    summary = generator.generate_summary_report(deps.knowledge_graph)
    console.print("\n" + "="*60)
    console.print(Markdown(summary))
    console.print("="*60 + "\n")
    
    return output_path


async def run_full_pipeline_cli(video_path: Path, output_filename: str):
    """Run the complete pipeline from CLI."""
    console.print(Panel.fit(
        "[bold cyan]Video Analysis Agent - Full Pipeline[/bold cyan]\n"
        f"Video: {video_path.name}",
        border_style="cyan"
    ))
    
    # Initialize dependencies
    settings = load_settings()
    deps = AgentDependencies(settings=settings)
    await deps.initialize()
    deps.set_video_path(str(video_path))
    
    try:
        # Stage 1: Gemini
        await run_gemini_stage(video_path, deps)
        
        # Stage 2: Whisper
        await run_whisper_stage(video_path, deps)
        
        # Stage 3: Chunking
        await run_chunking_stage(deps)
        
        # Stage 4: Knowledge Graph
        await run_knowledge_graph_stage(deps)
        
        # Stage 5: System Prompt
        output_path = await run_system_prompt_stage(deps, output_filename)
        
        console.print("\n[bold green]✓ Pipeline completed successfully![/bold green]")
        console.print(f"\n[bold]Output:[/bold] {output_path}")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Pipeline failed: {e}[/bold red]")
        logger.exception("Pipeline error")
    finally:
        await deps.cleanup()


async def run_individual_stage(
    stage: str,
    video_path: Path,
    output_filename: Optional[str] = None
):
    """Run an individual processing stage."""
    console.print(Panel.fit(
        f"[bold cyan]Video Analysis Agent - {stage.title()} Stage[/bold cyan]\n"
        f"Video: {video_path.name}",
        border_style="cyan"
    ))
    
    # Initialize dependencies
    settings = load_settings()
    deps = AgentDependencies(settings=settings)
    await deps.initialize()
    deps.set_video_path(str(video_path))
    
    try:
        if stage == "gemini":
            await run_gemini_stage(video_path, deps)
        elif stage == "whisper":
            await run_whisper_stage(video_path, deps)
        elif stage == "chunking":
            await run_chunking_stage(deps)
        elif stage == "knowledge_graph":
            await run_knowledge_graph_stage(deps)
        elif stage == "system_prompt":
            output_name = output_filename or "system_prompt.txt"
            await run_system_prompt_stage(deps, output_name)
        
        console.print(f"\n[bold green]✓ {stage.title()} stage completed![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ {stage.title()} stage failed: {e}[/bold red]")
        logger.exception("Stage error")
    finally:
        await deps.cleanup()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Video Analysis Agent - Extract trading knowledge from videos"
    )
    
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to video file"
    )
    
    parser.add_argument(
        "--stage",
        choices=["gemini", "whisper", "chunking", "knowledge_graph", "system_prompt", "full"],
        default="full",
        help="Processing stage to run (default: full pipeline)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="system_prompt.txt",
        help="Output filename for system prompt (default: system_prompt.txt)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate video path
    video_path = Path(args.video_path)
    if not video_path.exists():
        console.print(f"[red]Error: Video file not found: {video_path}[/red]")
        sys.exit(1)
    
    # Run requested stage(s)
    if args.stage == "full":
        asyncio.run(run_full_pipeline_cli(video_path, args.output))
    else:
        asyncio.run(run_individual_stage(args.stage, video_path, args.output))


if __name__ == "__main__":
    main()
