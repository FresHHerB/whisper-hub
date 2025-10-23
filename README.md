# OpenAI Whisper Official - RunPod Serverless Worker

[![Runpod](https://api.runpod.io/badge/FresHHerB/whisper-hub)](https://console.runpod.io/hub/FresHHerB/whisper-hub)

RunPod serverless worker for audio transcription using **OpenAI Whisper Official** (PyTorch implementation).

## Features

- ✅ **OpenAI Whisper Official** (maximum quality, no quantization)
- ✅ **GPU-optimized** (CUDA 11.8, PyTorch 2.1.2, FP16, TF32)
- ✅ **Pre-cached models** (base, medium, turbo) for fast cold starts (~30s-2min)
- ✅ **Word-level timestamps** (karaoke-style synchronization)
- ✅ **Automatic language detection** or manual specification
- ✅ **Thread-safe** model loading with caching

---

## Available Models

| Model | Parameters | VRAM (FP16) | Speed | Quality | Use Case |
|-------|-----------|-------------|-------|---------|----------|
| **base** | 74M | ~1.5GB | Fast | Good | **General use** ⭐ |
| **medium** | 769M | ~5GB | Moderate | Excellent | High quality |
| **turbo** | 809M | ~6GB | Fast | Excellent | **Best balance** ⭐ |

**Pre-cached in image:** base, medium, turbo
**Also available:** tiny, small, large-v1, large-v2, large-v3 (downloaded on first use)

---

## Input Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `audio` | string | **Required**. URL to audio file (mp3, wav, m4a, flac, etc.) |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `"base"` | Whisper model to use (`base`, `medium`, `turbo`, etc.) |
| `language` | string | `null` | Language code (e.g., `"pt"`, `"en"`) or `null` for auto-detect |
| `temperature` | float | `0.0` | Sampling temperature (0.0-1.0). Higher = more random |
| `beam_size` | int | `5` | Beam search size (1-10). Higher = slower but more accurate |
| `word_timestamps` | boolean | `false` | Enable word-level timestamps (for karaoke/highlighting) |

---

## Output Format

```json
{
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, welcome to the video",
      "tokens": [1234, 5678, ...],
      "temperature": 0.0,
      "avg_logprob": -0.234,
      "compression_ratio": 1.8,
      "no_speech_prob": 0.01
    }
  ],
  "word_timestamps": [
    {"word": "Hello", "start": 0.0, "end": 0.5},
    {"word": "welcome", "start": 0.6, "end": 1.2}
  ],
  "detected_language": "en",
  "transcription": "Hello, welcome to the video...",
  "device": "cuda",
  "model": "base"
}
```

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `segments` | array | Transcription segments with timestamps and metadata |
| `word_timestamps` | array | Word-level timestamps (only if `word_timestamps: true`) |
| `detected_language` | string | ISO 639-1 language code (e.g., "pt", "en") |
| `transcription` | string | Full transcription text |
| `device` | string | Device used ("cuda" or "cpu") |
| `model` | string | Model used for transcription |

---

## Usage Examples

### Basic Transcription

```json
{
  "input": {
    "audio": "https://example.com/audio.mp3",
    "model": "base"
  }
}
```

### Portuguese with Word Timestamps

```json
{
  "input": {
    "audio": "https://example.com/audio.mp3",
    "model": "turbo",
    "language": "pt",
    "word_timestamps": true
  }
}
```

### High Quality (Medium Model)

```json
{
  "input": {
    "audio": "https://example.com/audio.mp3",
    "model": "medium",
    "beam_size": 10,
    "temperature": 0.0
  }
}
```

---

## Performance

### Cold Start Times

| Scenario | Time | Notes |
|----------|------|-------|
| **First start** (cached model) | ~30s-2min | Image pull + model load |
| **FlashBoot** (warm worker) | ~10-20s | Worker reactivated |
| **Active worker** | <5s | Worker already running |

### Transcription Speed

GPU: RTX 4090, Model: base

| Audio Length | Processing Time | RTF (Real-Time Factor) |
|--------------|----------------|------------------------|
| 1 min | ~2-3s | 0.03-0.05x |
| 10 min | ~15-25s | 0.025-0.04x |
| 30 min | ~45-75s | 0.025-0.04x |

**RTF < 0.1x** = Very fast (10 min audio in 1 min)

---

## Deployment to RunPod Hub

### Prerequisites

Before publishing to RunPod Hub, ensure you have:
- ✅ GitHub repository with all required files
- ✅ `.runpod/hub.json` - Hub configuration
- ✅ `.runpod/tests.json` - Test cases
- ✅ `Dockerfile` - Container definition
- ✅ `src/handler.py` - RunPod serverless handler
- ✅ RunPod Hub badge in README.md

### Step 1: Fork/Clone Repository

```bash
# Fork this repository on GitHub
# Or create your own repo and copy files

git clone https://github.com/YOUR_USERNAME/whisper-hub.git
cd whisper-hub
```

### Step 2: Connect to RunPod Hub

1. Go to [RunPod Console](https://console.runpod.io) → **Hub** → **My Repos**
2. Click **Add Repository**
3. Connect your GitHub account if not already connected
4. Select your `whisper-hub` repository
5. RunPod will validate the configuration files:
   - `.runpod/hub.json` ✅
   - `.runpod/tests.json` ✅
   - `Dockerfile` ✅

### Step 3: Create a GitHub Release

**IMPORTANT:** RunPod Hub requires a GitHub release to publish your changes.

```bash
# Commit your changes
git add .
git commit -m "feat: initial RunPod Hub configuration"
git push origin main

# Create and push a tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial RunPod Hub release"
git push origin v1.0.0

# Or create release via GitHub UI:
# https://github.com/YOUR_USERNAME/whisper-hub/releases/new
# - Tag version: v1.0.0
# - Release title: v1.0.0 - Initial Release
# - Description: OpenAI Whisper Official worker for RunPod Serverless
```

### Step 4: Publish to Hub

1. Go to your repo on RunPod Hub
2. Click **Publish Release**
3. Select the release tag (e.g., `v1.0.0`)
4. RunPod will:
   - Build Docker image (~10-15 min)
   - Run automated tests from `.runpod/tests.json`
   - Publish to public hub if tests pass

### Step 5: Deploy Serverless Endpoint

Once published, you can deploy an endpoint:

1. Go to **Serverless** → **Create Endpoint**
2. **Template Selection:**
   - Browse Hub → Search "OpenAI Whisper Official"
   - Or **Your Repos** → `whisper-hub`
3. **Configuration:**
   - Name: `whisper-official`
   - Min Workers: `0` (pay-per-use) or `1` (always ready)
   - Max Workers: `3-5`
   - GPU Types: `AMPERE_16`, `AMPERE_24`, `NVIDIA RTX A4000`
   - Idle Timeout: `30s`
   - FlashBoot: `Enabled` (recommended)
4. Click **Deploy**
5. Copy **Endpoint ID** (e.g., `abc123xyz`)

### Step 6: Test Your Endpoint

```bash
# Test with JFK audio sample
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "audio": "https://github.com/openai/whisper/raw/main/tests/jfk.flac",
      "model": "base",
      "word_timestamps": true
    }
  }'

# Check status
curl "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Updating Your Hub Listing

To update your hub listing:

1. Make changes to your code/configuration
2. Commit and push changes
3. Create a new GitHub release (e.g., `v1.1.0`)
4. RunPod will automatically detect and build the new release
5. Users can select which version to deploy

---

## Architecture

### Directory Structure

```
whisper-hub/
├── Dockerfile                # GPU worker with CUDA + PyTorch + Whisper
├── requirements.txt          # Runtime dependencies (runpod, requests)
├── test_input.json          # Test request payload
├── README.md                # This file
├── builder/
│   ├── fetch_models.py      # Pre-download models during build
│   └── requirements.txt     # Build dependencies
└── src/
    ├── handler.py           # RunPod serverless handler (entry point)
    └── predict.py           # Predictor class (model management)
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **handler.py** | RunPod job handling, audio download, input validation |
| **predict.py** | Model loading, caching, GPU optimization, transcription |
| **fetch_models.py** | Pre-download models during Docker build |
| **Dockerfile** | CUDA + PyTorch + Whisper installation, model pre-caching |

### Worker vs Orchestrator

**Worker (this repo):**
- ✅ Audio download
- ✅ Transcription with Whisper
- ✅ Language detection
- ✅ Segment generation
- ✅ Word timestamps generation
- ❌ NO file formatting (SRT, ASS, JSON)
- ❌ NO S3 upload

**Orchestrator (separate):**
- ✅ Calls worker via RunPod API
- ✅ Formats output (SRT, ASS, JSON)
- ✅ S3/MinIO upload
- ✅ Final response construction

---

## GPU Optimizations

### Automatic Optimizations

1. **FP16 Inference** (50% VRAM reduction, 2x faster)
   ```python
   fp16=True if device=="cuda" else False
   ```

2. **TF32 on Ampere GPUs** (~30% speedup on RTX 30xx, A100)
   ```python
   torch.backends.cuda.matmul.allow_tf32 = True
   ```

3. **Model Caching** (load once, reuse)
   ```python
   # Models cached between requests
   # Only reloads if different model requested
   ```

### VRAM Usage

| Model | VRAM (FP16) | VRAM (FP32) |
|-------|-------------|-------------|
| base | ~1.5GB | ~3GB |
| medium | ~5GB | ~10GB |
| turbo | ~6GB | ~12GB |

**Recommended GPUs:**
- RTX 4000 (16GB): base, medium, turbo
- RTX A4000 (16GB): base, medium, turbo
- RTX 4090 (24GB): All models
- A100 (40GB/80GB): All models

---

## Troubleshooting

### "Out of GPU memory"
**Solution:** Use smaller model or GPU with more VRAM
- 8GB GPU: tiny, base
- 16GB GPU: tiny, base, medium, turbo
- 24GB+ GPU: all models

### Worker takes 8+ minutes (first time)
**Normal!** First job includes:
1. RunPod starts worker (1-2 min)
2. Pull Docker image (30s-2min if cached)
3. Load model to GPU (5-10s)

Subsequent jobs are much faster (~20-40s).

### "Model not found"
**Solution:** Model will be downloaded on first use. Pre-cached models (base, medium, turbo) load instantly. Other models (tiny, small, large-v1/v2/v3) download on first request (~30s-2min).

---

## License

MIT License

## Credits

- **OpenAI Whisper:** https://github.com/openai/whisper
- **RunPod:** https://runpod.io
- **Based on:** runpod-workers/worker-faster_whisper architecture

---

## Support

For issues or questions:
- Create an issue on GitHub
- Check RunPod documentation: https://docs.runpod.io
