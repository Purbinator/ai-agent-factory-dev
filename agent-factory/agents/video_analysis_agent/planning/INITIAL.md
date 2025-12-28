# Video Analysis Agent - Initial Requirements

## 📋 Project Overview

**Agent Name**: Video Analysis Agent  
**Purpose**: Lossless knowledge extraction from trading/orderflow videos  
**Approach**: 3-channel hybrid pipeline (Gemini + Whisper + Semantic Chunking)

## 🎯 Core Functionality

### 1. Gemini Video Processing
- Process 60+ minute videos at 1 FPS using Gemini 1.5 Pro
- Extract visual orderflow patterns with timestamps
- Identify DOM imbalances, volume surges, price breaks
- Capture visual markers and emphasis points

### 2. Whisper Transcription
- Word-level timestamp transcription (millisecond precision)
- Extract trader intent and verbal emphasis
- Identify action triggers and hesitation markers
- Support both local model and API mode

### 3. Semantic Chunking
- Identify logical orderflow segments
- Detect state changes (imbalance, price breaks, volume shifts)
- Align visual and audio boundaries
- Classify segment types (explanation, setup, execution, review)

### 4. Knowledge Graph Assembly
- Merge all analysis into unified structure
- Build 4 layers:
  - Complete timeline (visual + audio events)
  - Orderflow rules (patterns + success rates)
  - Pattern signatures (visual + audio pairs)
  - Confidence matrix (scoring rules)

### 5. System Prompt Generation
- Transform knowledge graph into production-ready prompt
- Human-readable + machine-parseable format
- Include timeline references, rules, patterns, decision framework
- Output to `output/system_prompt.txt`

## 🔧 Technical Requirements

### APIs & Models
- **Gemini**: 1.5 Pro with 1M token context
- **Whisper**: large-v3 model (local or API)
- **LLM**: OpenAI-compatible for agent orchestration

### Dependencies
- google-generativeai
- openai
- pydantic-ai
- rich (CLI)
- ffmpeg (audio extraction)

### Processing Stages
1. Gemini video analysis
2. Whisper transcription
3. Semantic chunking
4. Knowledge graph building
5. System prompt generation

Can run individual stages or full pipeline.

## 🎨 User Interface

### CLI Commands
```bash
# Full pipeline
python cli.py video.mp4

# Individual stages
python cli.py video.mp4 --stage gemini
python cli.py video.mp4 --stage whisper
python cli.py video.mp4 --stage chunking
python cli.py video.mp4 --stage knowledge_graph
python cli.py video.mp4 --stage system_prompt
```

### Configuration
- Environment variables via `.env` file
- Pydantic Settings for validation
- Support for API keys, model selection, processing parameters

## 📊 Expected Output

### system_prompt.txt
- Trading overview
- Timeline reference with key moments
- Core rules with confidence scores
- Pattern library with visual + audio signatures
- Decision framework with if-then logic
- Risk management guidelines

### system_prompt.json
- Structured knowledge graph for machine parsing

## ✅ Success Criteria

1. Process 60+ minute videos successfully
2. Extract patterns with <5% information loss
3. Generate actionable trading rules
4. Cross-modal validation (visual + audio alignment)
5. Production-ready system prompt output

## 🚀 Future Enhancements

- CLIP-based visual embeddings for better chunking
- Pattern success rate tracking
- Multi-video knowledge aggregation
- Real-time video analysis mode
- Database integration for knowledge persistence
