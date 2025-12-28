# Video Analysis Agent

Lossless video knowledge extraction agent using Gemini 1.5 Pro and Whisper for trading/orderflow videos.

## 🎯 Overview

This agent implements a 3-channel hybrid approach to extract complete knowledge from trading videos with **~2% information loss** (only from Gemini API compression):

1. **Dense Multimodal Video Understanding**: Gemini 1.5 Pro processes 60+ minute videos natively at 1 FPS
2. **Precision Whisper Transcription**: Word-level timestamp transcription of trader speech/intent
3. **Semantic Knowledge Graph**: Intelligent chunking and knowledge graph assembly

### ⚡ Orderflow Trading Optimization

**Enhanced for orderflow/DOM trading videos** with:
- DOM (Depth of Market) data extraction (bid/ask ratios, order sizes)
- Pattern recognition library (absorption, delta divergence, liquidity sweeps)
- **Success rate tracking** from observable outcomes
- Cross-modal validation (visual + audio alignment)
- Quantified data extraction (prices, volumes, ratios)

👉 **See [ORDERFLOW_GUIDE.md](ORDERFLOW_GUIDE.md) for detailed trading-specific documentation**

## 📋 Features

- **5-Stage Pipeline**:
  - Phase 1: Gemini video analysis (visual orderflow dynamics + DOM data)
  - Phase 2: Whisper transcription (trader speech with timestamps)
  - Phase 3: Semantic chunking (orderflow-aware segmentation)
  - Phase 4: Knowledge graph assembly (timeline + rules + signatures + outcomes)
  - Phase 5: System prompt generation (production-ready output)

- **Outputs**:
  - Complete timeline with exact timestamps
  - Orderflow rules with **success rates** (tracked from outcomes)
  - Pattern signature library (visual + audio confirmations)
  - Cross-modal confidence matrix
  - Human-readable system prompt + JSON knowledge graph

- **Orderflow Patterns Supported**:
  - Absorption patterns
  - Delta divergence
  - Liquidity sweeps
  - DOM imbalances
  - Iceberg orders
  - Volume climax

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key
- OpenAI API key (if using Whisper API)
- ffmpeg (for audio extraction)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install ffmpeg (required for audio extraction):
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

3. (Optional) Install local Whisper:
```bash
pip install openai-whisper
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file with your settings:

```env
# Required
GEMINI_API_KEY=your-gemini-api-key-here
LLM_API_KEY=your-llm-api-key-here

# Optional (for Whisper API mode)
WHISPER_API_KEY=your-openai-api-key-here
WHISPER_USE_API=false  # Set to true to use API instead of local
```

## 📖 Usage

### Full Pipeline (Recommended)

Process a video through all stages:

```bash
python cli.py /path/to/video.mp4
```

Or with options:

```bash
python cli.py /path/to/video.mp4 --output my_system_prompt.txt --verbose
```

### Individual Stages

Run specific processing stages:

```bash
# Stage 1: Gemini video analysis
python cli.py /path/to/video.mp4 --stage gemini

# Stage 2: Whisper transcription
python cli.py /path/to/video.mp4 --stage whisper

# Stage 3: Semantic chunking
python cli.py /path/to/video.mp4 --stage chunking

# Stage 4: Knowledge graph assembly
python cli.py /path/to/video.mp4 --stage knowledge_graph

# Stage 5: System prompt generation
python cli.py /path/to/video.mp4 --stage system_prompt --output output.txt
```

### Python API

Use the agent programmatically:

```python
import asyncio
from agent import video_analysis_agent
from dependencies import AgentDependencies

async def main():
    deps = AgentDependencies()
    await deps.initialize()
    
    result = await video_analysis_agent.run(
        "Analyze this trading video: /path/to/video.mp4",
        deps=deps
    )
    
    print(result.data)
    await deps.cleanup()

asyncio.run(main())
```

## 🏗️ Architecture

```
video_analysis_agent/
├── agent.py                 # Main agent definition
├── cli.py                   # CLI interface
├── prompts.py              # System prompts
├── tools.py                # Agent tools
├── providers.py            # API providers
├── dependencies.py         # Dependency injection
├── settings.py             # Configuration
├── ingestion/              # Processing pipeline
│   ├── video_processor.py       # Gemini video analysis
│   ├── transcriber.py           # Whisper transcription
│   ├── semantic_chunker.py      # Intelligent segmentation
│   ├── knowledge_graph_builder.py  # KG assembly
│   └── system_prompt_generator.py  # Prompt generation
├── tests/                  # Test suite
└── output/                 # Generated outputs
```

## 🔧 Processing Pipeline Details

### Phase 1: Gemini Video Analysis

- Processes video at 1 FPS with 1M token context
- Extracts:
  - Visual orderflow patterns
  - DOM imbalances and spread changes
  - Timeline events with timestamps
  - Cross-modal validation points

### Phase 2: Whisper Transcription

- Word-level timestamp precision (milliseconds)
- Extracts:
  - Complete transcript with timing
  - Trader intent statements
  - Emphasis patterns (repetitions, tone)
  - Action triggers ("now", "watch this")

### Phase 3: Semantic Chunking

- Identifies logical segment boundaries:
  - New DOM imbalance patterns
  - Price level breaks
  - Volume surges
  - Trader behavior shifts
- Classifies segments (explanation, setup, execution, review)

### Phase 4: Knowledge Graph Assembly

Builds 4-layer knowledge structure:

1. **Complete Timeline**: Chronological events with visual + audio alignment
2. **Orderflow Rules**: Patterns with success rates and conditions
3. **Pattern Signatures**: Visual/audio pairs with occurrence counts
4. **Confidence Matrix**: Scoring rules for decision-making

### Phase 5: System Prompt Generation

Generates human-readable + machine-parseable output:

- Trading overview and approach
- Timeline reference with timestamps
- Core rules with confidence scores
- Pattern library with signatures
- Decision framework (if-then logic)
- Risk management guidelines

## 📊 Output Format

### system_prompt.txt

```
# Trading System Prompt
Generated from: video.mp4
Date: 2024-12-28

## OVERVIEW
This system encodes knowledge from 127 events...

## CORE TRADING RULES

### RULE_001: DOM Imbalance Pattern
Confidence: 0.85 | Occurrences: 5
Description: Large buy orders at support level...

## PATTERN LIBRARY

### PAT_001: Volume Surge Pattern
Reliability: 0.78 | Occurrences: 8
Visual Signatures:
  - Green volume bars 3x average
  - Price at resistance
Audio Confirmations:
  - "big volume here"
  - "watch this level"
```

### system_prompt.json

Structured JSON with complete knowledge graph for machine parsing.

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_gemini_video_processor.py

# With coverage
pytest --cov=. tests/
```

## 🔍 Troubleshooting

### ffmpeg not found

Install ffmpeg for your platform (see Installation section).

### Gemini API quota exceeded

- Check your API quota in Google Cloud Console
- Consider processing videos in shorter chunks
- Reduce FPS extraction rate in settings

### Whisper local model too slow

- Use Whisper API mode: `WHISPER_USE_API=true`
- Or use smaller model: `WHISPER_MODEL=base`

### Out of memory

- Reduce video resolution before processing
- Process video in chunks
- Use smaller Whisper model

## ⚙️ Configuration Options

Key settings in `.env`:

```env
# Video processing
VIDEO_FPS_EXTRACTION=1              # Lower for faster processing
VIDEO_MAX_DURATION_MINUTES=120      # Maximum video length

# Semantic chunking
CHUNK_MIN_DURATION_SECONDS=5        # Minimum segment length
CHUNK_MAX_DURATION_SECONDS=300      # Maximum segment length
CHUNK_SIMILARITY_THRESHOLD=0.75     # Higher = fewer segments

# Knowledge graph
KG_MIN_PATTERN_OCCURRENCES=2        # Minimum pattern occurrences
KG_CONFIDENCE_THRESHOLD=0.6         # Minimum confidence for rules
```

## 📝 Examples

### Example 1: Quick Analysis

```bash
python cli.py trading_session.mp4
```

### Example 2: High-Quality Transcription

```bash
# Edit .env
WHISPER_MODEL=large-v3
WHISPER_USE_API=true

python cli.py trading_session.mp4 --verbose
```

### Example 3: Custom Output

```bash
python cli.py trading_session.mp4 --output custom_prompt.txt
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

- Code follows PEP8 style
- All tests pass
- New features include tests
- Docstrings use Google style

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini 1.5 Pro for multimodal video understanding
- OpenAI Whisper for precision transcription
- Pydantic AI for agent framework

## 📚 Further Reading

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Whisper Documentation](https://github.com/openai/whisper)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)

---

**Need help?** Check the examples in `examples/` or open an issue.
