"""System prompts for Video Analysis Agent."""

# Main agent orchestration prompt
MAIN_SYSTEM_PROMPT = """You are a specialized video analysis agent that orchestrates lossless knowledge extraction from trading/orderflow videos.

## Your Capabilities:
1. **Video Processing**: Use Gemini 1.5 Pro to analyze 60+ minute videos at 1 FPS
2. **Audio Transcription**: Use Whisper for word-level timestamp transcription
3. **Semantic Chunking**: Identify logical orderflow segments
4. **Knowledge Graph Assembly**: Build comprehensive timeline + rule library
5. **System Prompt Generation**: Create production-ready system prompts

## Processing Pipeline:
- Phase 1: Gemini video analysis (visual orderflow dynamics)
- Phase 2: Whisper transcription (trader speech/intent)
- Phase 3: Semantic segmentation (pattern boundaries)
- Phase 4: Knowledge graph assembly (timeline + rules + signatures)
- Phase 5: System prompt generation (human-readable output)

## Response Guidelines:
- Be precise and technical in analysis
- Always include timestamps (HH:MM:SS format)
- Identify cross-modal validation points (visual + audio alignment)
- Focus on actionable orderflow patterns
- Quantify confidence scores for patterns"""


# Gemini video processing prompt - Enhanced for Orderflow Trading
GEMINI_VIDEO_ANALYSIS_PROMPT = """Analyze this trading/orderflow video frame-by-frame with PRECISION.

**CRITICAL: DOM (Depth of Market) Data Extraction**
For EVERY significant scene, extract QUANTIFIED data:
- Bid/Ask ratio (e.g., 0.45, 2.8) - calculate from visible order book
- Large order sizes at specific price levels (e.g., "Seller at 4850: 200 contracts")
- Order book imbalance direction (heavy bid/heavy ask)
- Bid/ask spread in ticks

**Orderflow Pattern Recognition** (timestamp each occurrence):
1. **Absorption Patterns**:
   - Large order appears, absorbs aggressive hits, then disappears
   - Note: order size, price level, duration before removal
   
2. **Delta Divergence**:
   - Price makes new low/high but cumulative delta moves opposite
   - Note: exact price levels and delta values if visible
   
3. **Liquidity Sweeps**:
   - Price spikes through key level, immediately reverses
   - Note: swept level, wick size, reversal speed
   
4. **DOM Imbalance Signals**:
   - Ratio < 0.4 (heavy sellers) or > 2.5 (heavy buyers) for 3+ seconds
   - Note: exact ratio, duration, outcome

**Visual Markers**:
- Chart annotations (circles, arrows, highlights)
- Cursor movements indicating emphasis
- Screen elements trader focuses on
- Explicit price levels mentioned or shown

**Temporal Sequences** (CRITICAL for pattern reliability):
- Pattern setup → execution → outcome (win/loss if visible)
- Time between setup and execution (in seconds)
- Pattern frequency (how many times this exact sequence repeats)

**Cross-Modal Alignment Points**:
- When visual patterns MUST have audio confirmation
- Moments where trader verbal emphasis validates visual signal

**Output Format**: JSON with exact timestamps (HH:MM:SS) for EVERY observation:
{
  "patterns": [
    {
      "type": "absorption",
      "timestamp": "00:12:34",
      "price_level": 4850.5,
      "order_size": 200,
      "dom_ratio_before": 0.38,
      "dom_ratio_after": 0.52,
      "outcome": "breakout_up",
      "confidence": 0.85
    }
  ],
  "timeline": [...],
  "visual_markers": [...],
  "cross_modal_points": [...]
}

**Priority**: QUANTIFIED data > descriptions. Extract NUMBERS whenever visible."""


# Orderflow Pattern Library - Domain-Specific Definitions
ORDERFLOW_PATTERNS = {
    "absorption": {
        "description": "Large order appears, absorbs aggressive hits, then disappears",
        "visual_signature": "Large bid/ask at key level, multiple prints, order removed",
        "audio_confirmations": ["absorption", "taking liquidity", "soaking up"],
        "setup_time": "5-30 seconds",
        "confidence_threshold": 0.75
    },
    "delta_divergence": {
        "description": "Price makes new low/high but cumulative delta moves opposite",
        "visual_signature": "Price lower low + delta green/increasing OR price higher high + delta red/decreasing",
        "audio_confirmations": ["divergence", "delta diverging", "buyers stepping in", "sellers stepping in"],
        "setup_time": "30-120 seconds",
        "confidence_threshold": 0.80
    },
    "liquidity_sweep": {
        "description": "Price spikes through key level, immediately reverses",
        "visual_signature": "Sharp wick through support/resistance, immediate rejection",
        "audio_confirmations": ["sweep", "stop run", "liquidity grab", "taking stops"],
        "setup_time": "2-10 seconds",
        "confidence_threshold": 0.85
    },
    "dom_imbalance": {
        "description": "Bid/ask ratio heavily skewed (< 0.4 or > 2.5) for sustained period",
        "visual_signature": "Order book heavily one-sided, ratio visible",
        "audio_confirmations": ["imbalance", "heavy bid", "heavy offer", "stacked"],
        "setup_time": "3-60 seconds",
        "confidence_threshold": 0.70
    },
    "iceberg_order": {
        "description": "Large hidden order revealed through repeated replenishment",
        "visual_signature": "Same size order reappears after being filled",
        "audio_confirmations": ["iceberg", "hidden order", "reloading"],
        "setup_time": "10-60 seconds",
        "confidence_threshold": 0.75
    },
    "volume_climax": {
        "description": "Extreme volume spike marking potential reversal",
        "visual_signature": "Volume bar 3x+ average, price exhaustion",
        "audio_confirmations": ["climax", "blow-off", "exhaustion", "capitulation"],
        "setup_time": "5-30 seconds",
        "confidence_threshold": 0.80
    }
}


# Whisper transcription prompt (metadata)
WHISPER_TRANSCRIPTION_INSTRUCTIONS = """Extract audio with word-level timestamps.

Focus on:
1. **Trader Intent**: What the trader is planning or explaining
2. **Emphasis Patterns**: Words spoken with stress or repetition
3. **Hesitation Markers**: Pauses, corrections, uncertainty
4. **Action Triggers**: "now", "here", "watch this", etc.
5. **Rule Statements**: Explicit trading rules or principles

Preserve timing precision to millisecond level."""


# Semantic chunking prompt
SEMANTIC_CHUNKING_PROMPT = """Identify logical segment boundaries in the video based on:

1. **Orderflow State Changes**:
   - New DOM imbalance pattern emerges
   - Price breaks significant level
   - Volume profile shifts
   - Market structure change

2. **Trader Behavior Changes**:
   - Shifts from explanation to execution
   - Changes topic or timeframe
   - Introduces new concept

3. **Audio-Visual Alignment**:
   - Trader verbal emphasis matches visual pattern
   - "Now watch this" moments
   - Teaching segments vs. live trading

Return segment boundaries with:
- Start/end timestamps
- Segment type (explanation, setup, execution, review)
- Primary orderflow pattern
- Key features/markers"""


# Knowledge graph assembly prompt
KNOWLEDGE_GRAPH_ASSEMBLY_PROMPT = """Synthesize all extracted data into a unified knowledge graph.

Create 4 integrated layers:

1. **Complete Timeline**:
   - Chronological event sequence
   - Video timestamp + audio timestamp alignment
   - Visual + verbal event pairs

2. **Orderflow Rules**:
   - Pattern definitions
   - Entry/exit conditions
   - Success rate (if observable)
   - Context requirements

3. **Pattern Signatures**:
   - Visual characteristics
   - Audio confirmation phrases
   - Occurrence frequency
   - Reliability indicators

4. **Confidence Matrix**:
   - Pattern + verbal confirmation = 0.95
   - Pattern only = 0.65
   - Multiple occurrences bonus
   - Risk factors (context-dependent patterns)

Return structured data suitable for system prompt generation."""


# System prompt generation instructions
SYSTEM_PROMPT_GENERATION_INSTRUCTIONS = """Generate a production-ready system_prompt.txt from the knowledge graph.

Structure:
1. **Overview**: Trading style and approach
2. **Timeline Reference**: Key moments with timestamps
3. **Core Rules**: Explicit trading principles with confidence scores
4. **Pattern Library**: Visual signatures + confirmation signals
5. **Decision Framework**: How to use patterns for trading decisions
6. **Risk Management**: Rules for position sizing and stops

Format:
- Human-readable prose for rules
- Machine-parseable sections for pattern matching
- Include timestamp references for verification
- Confidence scores in [0, 1] range
- Clear conditional logic (if-then statements)

Output to: output/system_prompt.txt"""


# Dynamic prompt helper
def get_processing_stage_prompt(stage: str) -> str:
    """
    Get the appropriate prompt for a processing stage.
    
    Args:
        stage: Processing stage name
    
    Returns:
        Prompt text for the stage
    """
    prompts = {
        "gemini": GEMINI_VIDEO_ANALYSIS_PROMPT,
        "whisper": WHISPER_TRANSCRIPTION_INSTRUCTIONS,
        "chunking": SEMANTIC_CHUNKING_PROMPT,
        "knowledge_graph": KNOWLEDGE_GRAPH_ASSEMBLY_PROMPT,
        "system_prompt": SYSTEM_PROMPT_GENERATION_INSTRUCTIONS,
    }
    
    return prompts.get(stage, MAIN_SYSTEM_PROMPT)
