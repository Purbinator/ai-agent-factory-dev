# Orderflow Trading Video Analysis Guide

## 🎯 Overview

This agent is specifically optimized for **orderflow/DOM trading video analysis** with enhanced capabilities for:
- DOM (Depth of Market) data extraction
- Trading pattern recognition (absorption, delta divergence, liquidity sweeps)
- Success rate tracking from video outcomes
- Cross-modal validation (visual + audio)

## 📊 What Gets Extracted

### 1. Complete Timeline (Exact Timestamps)

```
[00:12:34] Trader: "I see aggressive selling into resistance"
           DOM: Bid/Ask ratio 0.45, Large seller at 4850 (200 contracts)
           Chart: Price rejects wick at 4850.50
           Pattern: Rejection + Imbalance → Shorting setup (confidence: 0.85)

[00:12:35] Trader: "Classic absorption, they're taking liquidity"
           DOM: Seller removed, ratio rebalances to 0.52
           Chart: Lower wick rejection
           Pattern: Liquidity sweep + accumulation
           Outcome: Breakout_up (Success)
```

### 2. Orderflow Rules (With Success Rates)

```
RULE_001: DOM Absorption Pattern
  Pattern: absorption
  Description: Large order appears, absorbs hits, then disappears
  Occurrences: 5 times in video
  Success Rate: 80% (4/5 successful outcomes)
  Confidence: 0.82
  
  Entry Conditions:
    - DOM imbalance ratio 0.3-0.4
    - Large order visible at key level
    - Trader confirms "absorption" verbally
  
  Examples:
    [00:12:35] Absorption at 4850, outcome: breakout_up
    [00:45:12] Absorption at 5120, outcome: profit +15 ticks
    [01:23:45] Absorption at 4980, outcome: stop hit (loss)
```

### 3. Pattern Signature Library

```
Pattern: Delta Divergence
  Pattern ID: PAT_003
  Visual Signatures:
    - Price lower low
    - Cumulative delta increasingly positive
    - Volume divergence visible on histogram
  
  Audio Confirmations:
    - "bullish divergence forming"
    - "delta diverging"
    - "buyers stepping in"
  
  Occurrences: 3 times
  Success Rate: 100% (3/3)
  Reliability: 1.0
  
  Timestamps: [00:15:30, 00:32:45, 00:48:12]
```

### 4. Cross-Modal Confidence Matrix

```
Pattern Recognition Confidence Scoring:
- Pattern visual + audio confirmation: 0.95
- Pattern visual only: 0.65
- Multiple occurrences bonus: +0.05 per occurrence
- Quantified data present: +0.15 bonus

Examples:
  Scenario: "DOM imbalance 0.38" + trader says "absorption"
  → Confidence: 0.95

  Scenario: "DOM imbalance 0.38" + no verbal confirmation
  → Confidence: 0.65

  Scenario: Pattern seen 5+ times in video
  → Confidence: base + (0.05 × 5) = +0.25 boost
```

## 🚀 Usage

### Basic Pipeline

```bash
# Full pipeline - all stages
python cli.py /path/to/trading_video.mp4

# Output: output/system_prompt.txt + output/system_prompt.json
```

### Individual Stages

```bash
# Stage 1: Gemini video analysis (enhanced for orderflow)
python cli.py trading_video.mp4 --stage gemini

# Stage 2: Whisper transcription
python cli.py trading_video.mp4 --stage whisper

# Stage 3: Semantic chunking
python cli.py trading_video.mp4 --stage chunking

# Stage 4: Knowledge graph assembly
python cli.py trading_video.mp4 --stage knowledge_graph

# Stage 5: System prompt generation
python cli.py trading_video.mp4 --stage system_prompt --output orderflow_rules.txt
```

### Python API

```python
import asyncio
from agent import get_video_analysis_agent
from dependencies import AgentDependencies

async def analyze_trading_video():
    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()
    
    # Get the agent
    agent = get_video_analysis_agent()
    
    # Run analysis
    result = await agent.run(
        "Analyze this orderflow trading video and extract all patterns: /path/to/video.mp4",
        deps=deps
    )
    
    # Access extracted knowledge
    kg = deps.knowledge_graph
    
    # Print rules with success rates
    for rule in kg["orderflow_rules"]:
        print(f"\n{rule['rule_id']}: {rule['pattern_name']}")
        print(f"Success Rate: {rule['success_rate']}")
        print(f"Occurrences: {rule['occurrences']}")
        if rule.get("outcomes"):
            print(f"Outcomes: {len(rule['outcomes'])} tracked")
    
    await deps.cleanup()

asyncio.run(analyze_trading_video())
```

## 📋 Enhanced Prompts (Already Implemented)

### Gemini Prompt Enhancements

The agent now uses orderflow-specific prompts that extract:
1. **Quantified DOM data**: Exact bid/ask ratios, order sizes, price levels
2. **Pattern-specific markers**: Absorption, divergence, sweeps, imbalances
3. **Outcome tracking**: Success/failure of each pattern occurrence
4. **Temporal sequences**: Setup → execution → outcome timings

### Orderflow Pattern Library

Pre-configured pattern definitions:
- **Absorption**: Large order absorbs hits, then disappears
- **Delta Divergence**: Price vs cumulative delta divergence
- **Liquidity Sweep**: Price spikes through level, reverses
- **DOM Imbalance**: Ratio < 0.4 or > 2.5 for 3+ seconds
- **Iceberg Order**: Hidden order revealed through replenishment
- **Volume Climax**: Extreme volume spike marking reversal

## 🎓 Output Examples

### system_prompt.txt Structure

```
# Trading System Prompt
Generated from: orderflow_session_2024.mp4
Date: 2024-12-28 15:30:00

## OVERVIEW
This system encodes 127 video events, identifying 8 orderflow rules 
and 12 pattern signatures with tracked outcomes.

Approach: DOM-based orderflow trading using imbalances, absorption, 
and delta divergence patterns.

## CORE TRADING RULES

### RULE_001: DOM Absorption Entry
Confidence: 0.85 | Occurrences: 5 | Success Rate: 0.80 (4/5)

Description: When large order appears at key level, absorbs aggressive 
hits, then disappears → Entry signal

Entry Conditions:
  - DOM imbalance ratio 0.3-0.4
  - Large order size (100+ contracts)
  - Trader verbal confirmation "absorption"

Outcomes Tracked:
  - Successful: 4 (breakout, profit targets hit)
  - Failed: 1 (stop loss hit)

Examples:
  [00:12:35] Absorption at 4850 → breakout_up (+15 ticks)
  [00:45:12] Absorption at 5120 → profit target
  [01:23:45] Absorption at 4980 → stop hit (-8 ticks)

### RULE_002: Bullish Delta Divergence
Confidence: 0.92 | Occurrences: 3 | Success Rate: 1.00 (3/3)

Description: Price makes lower low but cumulative delta increases → Reversal signal

[... more rules ...]

## PATTERN LIBRARY

### PAT_003: Delta Divergence Pattern
Reliability: 1.0 | Occurrences: 3

Visual Signatures:
  - Price lower low visible on chart
  - Cumulative delta bar increasingly positive
  - Volume histogram divergence

Audio Confirmations:
  - "bullish divergence forming"
  - "buyers stepping in despite price"

Observed at: [00:15:30, 00:32:45, 00:48:12]

## DECISION FRAMEWORK

### Pattern Recognition Confidence Scores

Base Scores:
- Pattern visual only: 0.65
- Pattern + audio confirmation: 0.95
- Multiple occurrence bonus: +0.05 per occurrence
- Quantified data bonus: +0.15

### Decision Logic

IF pattern_confidence >= 0.95 AND success_rate >= 0.80:
    EXECUTE trade with full position size
ELIF pattern_confidence >= 0.80 AND success_rate >= 0.60:
    EXECUTE trade with 50% position size
ELIF pattern_confidence >= 0.65:
    MONITOR for additional confirmation
ELSE:
    SKIP (insufficient confidence)

## RISK MANAGEMENT

From Video Observations:
- Typical stop loss: 5-10 ticks below entry
- Risk/reward minimum: 1:2
- Position sizing: Based on pattern confidence × success rate
- Maximum risk per trade: 1-2% of account
```

### system_prompt.json Structure

```json
{
  "timeline": [
    {
      "timestamp": 754.5,
      "timestamp_str": "00:12:34",
      "event_type": "merged_event",
      "description": "Trader: 'aggressive selling' | DOM: ratio 0.45 | Pattern: rejection",
      "visual_data": {
        "dom_ratio": 0.45,
        "price_level": 4850.5,
        "pattern_type": "rejection"
      },
      "audio_data": {
        "text": "I see aggressive selling into resistance",
        "confidence": 0.95
      },
      "confidence": 0.9
    }
  ],
  "orderflow_rules": [
    {
      "rule_id": "RULE_001",
      "description": "DOM absorption pattern with imbalance",
      "pattern_name": "absorption",
      "occurrences": 5,
      "success_rate": 0.80,
      "confidence": 0.85,
      "outcomes": [
        {
          "success": true,
          "description": "breakout_up",
          "price_level": 4850.5,
          "dom_ratio": 0.38
        },
        {
          "success": false,
          "description": "stop_hit",
          "price_level": 4980.0,
          "dom_ratio": 0.42
        }
      ],
      "outcome_count": 5,
      "examples": [...]
    }
  ],
  "pattern_signatures": [...],
  "confidence_matrix": {
    "pattern_only": 0.65,
    "pattern_with_audio": 0.95,
    "average_rule_confidence": 0.82,
    "average_pattern_reliability": 0.75
  }
}
```

## 💡 Tips for Best Results

### Video Quality
- High resolution (1080p+) for clear DOM visibility
- Clear audio for trader commentary
- Stable frame rate (30+ FPS)

### Content
- Include trade outcomes (show P&L, stops, targets)
- Trader should verbalize strategy/intent
- Show DOM/order book clearly
- Multiple examples of same pattern (for success rate calculation)

### Processing
- First run: Use default settings
- Review output: Check if DOM ratios extracted correctly
- Refine: If needed, adjust confidence thresholds in settings

## 🔧 Configuration

Key settings in `.env`:

```env
# Gemini model (handles video analysis)
GEMINI_MODEL=gemini-1.5-pro-latest
GEMINI_TEMPERATURE=0.4

# Whisper (local for free processing)
WHISPER_USE_API=false
WHISPER_MODEL=large-v3

# Pattern detection thresholds
KG_MIN_PATTERN_OCCURRENCES=2
KG_CONFIDENCE_THRESHOLD=0.6

# Semantic chunking (orderflow-aware)
CHUNK_MIN_DURATION_SECONDS=5
CHUNK_MAX_DURATION_SECONDS=300
```

## 📊 Cost & Speed

For a 50-minute trading video:
- **Gemini 1.5 Pro**: 6-8 minutes, ~$15
- **Whisper (local)**: 3 minutes, $0
- **Knowledge Graph**: 2-3 minutes, $0
- **Total**: 11-14 minutes, ~$15

**Information Loss**: ~2% (only Gemini API compression, not architectural)

## 🎯 Use Cases

1. **Pattern Library Building**: Process multiple trading videos to build comprehensive pattern library
2. **Strategy Validation**: Quantify success rates of specific setups
3. **Training Material**: Convert video knowledge into system prompts for trading bots
4. **Performance Analysis**: Track which patterns work best in different market conditions

## 🚀 Next Steps

After processing:
1. Review `output/system_prompt.txt` for human-readable rules
2. Use `output/system_prompt.json` for programmatic access
3. Integrate rules into your trading system/bot
4. Combine multiple video analyses for comprehensive strategy

## ⚠️ Limitations

- DOM number accuracy depends on video quality
- Success rate calculation requires visible outcomes in video
- Pattern names/terminology depend on trader's vocabulary
- Works best with systematic, educational trading videos

## 📚 Further Reading

- See `README.md` for installation and setup
- See `PLANNING.md` for architecture details
- See `.env.example` for all configuration options
