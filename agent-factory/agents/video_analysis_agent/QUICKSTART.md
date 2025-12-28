# Quick Start Guide - Video Analysis Agent

Get started analyzing orderflow trading videos in 5 minutes.

## 🚀 Installation (2 minutes)

```bash
# 1. Navigate to agent directory
cd agent-factory/agents/video_analysis_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install ffmpeg (required for audio extraction)
# Ubuntu/Debian:
sudo apt-get install ffmpeg
# macOS:
brew install ffmpeg
# Windows: Download from https://ffmpeg.org

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys:
nano .env
```

## 🔑 Required API Keys

Add to `.env`:

```env
# Google Gemini (required for video analysis)
GEMINI_API_KEY=your-gemini-api-key-here

# LLM for agent orchestration
LLM_API_KEY=your-openai-api-key-here

# Whisper (optional - only if using API mode)
WHISPER_USE_API=false  # Use local model (free)
```

## 📹 Basic Usage (1 minute)

```bash
# Analyze a trading video (full pipeline)
python cli.py /path/to/trading_video.mp4

# That's it! Output in output/system_prompt.txt
```

## 📊 What You Get

After processing, check these files:

```bash
# Human-readable trading rules
cat output/system_prompt.txt

# Machine-parseable knowledge graph
cat output/system_prompt.json
```

### Example Output Structure

```
output/system_prompt.txt:
  ├─ Complete timeline with timestamps
  ├─ Orderflow rules with success rates
  ├─ Pattern library (visual + audio)
  ├─ Confidence matrix
  └─ Decision framework

output/system_prompt.json:
  ├─ Structured data for programming
  ├─ All rules, patterns, timelines
  └─ Success rates, outcomes
```

## 🎯 Common Use Cases

### 1. Quick Analysis

```bash
# Process and view results
python cli.py trading_session.mp4
cat output/system_prompt.txt
```

### 2. Individual Stages

```bash
# Just video analysis
python cli.py video.mp4 --stage gemini

# Just transcription
python cli.py video.mp4 --stage whisper

# Build knowledge graph
python cli.py video.mp4 --stage knowledge_graph
```

### 3. Custom Output

```bash
# Custom filename
python cli.py video.mp4 --output my_strategy.txt

# Verbose mode
python cli.py video.mp4 --verbose
```

### 4. Python API

```python
from agent import get_video_analysis_agent
from dependencies import AgentDependencies
import asyncio

async def analyze():
    deps = AgentDependencies()
    await deps.initialize()
    
    agent = get_video_analysis_agent()
    result = await agent.run(
        "Analyze this video: trading.mp4",
        deps=deps
    )
    
    # Access knowledge graph
    kg = deps.knowledge_graph
    print(f"Rules found: {len(kg['orderflow_rules'])}")
    
    await deps.cleanup()

asyncio.run(analyze())
```

## 🎓 Understanding Output

### Timeline Example
```
[00:12:34] Trader: "I see aggressive selling"
           DOM: Bid/Ask 0.45, Seller at 4850 (200 contracts)
           Pattern: Rejection + Imbalance
```

### Rule Example
```
RULE_001: DOM Absorption Pattern
  Success Rate: 80% (4/5 wins)
  Confidence: 0.85
  Occurrences: 5 times
```

### Pattern Example
```
PAT_003: Delta Divergence
  Visual: Price lower low + delta positive
  Audio: "bullish divergence forming"
  Reliability: 100% (3/3)
```

## ⚡ Tips for Best Results

### Video Quality
- ✅ Use 1080p+ resolution
- ✅ Clear DOM/order book visibility
- ✅ Stable 30+ FPS frame rate

### Content
- ✅ Trader verbalizes strategy
- ✅ Shows trade outcomes (P&L, stops, targets)
- ✅ Multiple examples of same patterns
- ✅ Clear audio commentary

### Settings
- ✅ Start with defaults
- ✅ Review output quality
- ✅ Adjust thresholds if needed

## 🔧 Troubleshooting

### Issue: "ffmpeg not found"
```bash
# Install ffmpeg for your OS (see Installation above)
```

### Issue: "Gemini API quota exceeded"
```bash
# Check Google Cloud Console for quota
# Consider processing shorter videos
# Reduce FPS: VIDEO_FPS_EXTRACTION=0.5 in .env
```

### Issue: "Whisper too slow"
```bash
# Use API mode or smaller model
WHISPER_USE_API=true  # or
WHISPER_MODEL=base    # Instead of large-v3
```

### Issue: "No success rates calculated"
```bash
# Video must show outcomes (wins/losses)
# Trader should mention "profit", "stop hit", etc.
# Or show P&L visibly
```

## 💰 Cost Expectations

For a 50-minute trading video:
- **Gemini 1.5 Pro**: ~$15 (6-8 minutes processing)
- **Whisper Local**: $0 (3 minutes processing)
- **Knowledge Graph**: $0 (2-3 minutes processing)
- **Total**: ~$15, 11-14 minutes

## 📚 Next Steps

1. **Process Your First Video**: Follow steps above
2. **Review Output**: Check `output/system_prompt.txt`
3. **Read Full Guide**: See `ORDERFLOW_GUIDE.md` for details
4. **Explore API**: Run `example_orderflow_analysis.py`
5. **Integrate**: Use system prompt in your trading bot

## 🆘 Need Help?

- **Setup Issues**: Check `README.md` Installation section
- **Trading-Specific**: Read `ORDERFLOW_GUIDE.md`
- **API Usage**: See `example_orderflow_analysis.py`
- **Architecture**: Review `PLANNING.md`
- **Enhancements**: See `ENHANCEMENTS.md`

## ⚡ Quick Reference

```bash
# Full pipeline
python cli.py video.mp4

# Gemini only
python cli.py video.mp4 --stage gemini

# With custom output
python cli.py video.mp4 --output my_rules.txt

# Verbose logging
python cli.py video.mp4 --verbose

# View results
cat output/system_prompt.txt

# Python API
python example_orderflow_analysis.py video.mp4
```

## ✅ Checklist

Before running:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] ffmpeg installed
- [ ] `.env` configured with API keys
- [ ] Video file ready (trading/orderflow content)

After running:
- [ ] Check `output/system_prompt.txt`
- [ ] Review success rates in rules
- [ ] Verify pattern signatures
- [ ] Check confidence matrix

## 🎯 Expected Results

After successful run:
- ✅ Complete timeline extracted
- ✅ Orderflow rules identified
- ✅ Success rates calculated (if outcomes visible)
- ✅ Pattern library built
- ✅ System prompt generated
- ✅ JSON knowledge graph created

**Information Loss**: ~2% (practically lossless)
**Processing Time**: 11-14 minutes (50min video)
**Cost**: ~$15 (Gemini API)

---

**Ready to analyze?** Run: `python cli.py your_trading_video.mp4`
