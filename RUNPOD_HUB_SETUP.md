# RunPod Hub Setup Guide

## ✅ Completed Steps

### 1. Repository Configuration
- ✅ Created `.runpod/hub.json` with complete Hub configuration
- ✅ Created `.runpod/tests.json` with 8 automated test cases
- ✅ Updated README.md with RunPod Hub badge
- ✅ Committed all changes to GitHub
- ✅ Created and pushed tag v1.0.0
- ✅ Published GitHub release v1.0.0

**GitHub Release:** https://github.com/FresHHerB/whisper-hub/releases/tag/v1.0.0

---

## 📋 Next Steps: Connect to RunPod Hub

### Option 1: Manual Setup via RunPod Console (Recommended)

1. **Access RunPod Hub**
   - Go to: https://console.runpod.io/hub
   - Login with your GitHub account (FresHHerB)

2. **Add Repository**
   - Click **"My Repos"** or **"Add Repository"**
   - Connect GitHub if not already connected
   - Select repository: `FresHHerB/whisper-hub`
   - RunPod will validate configuration files

3. **Publish Release**
   - Select tag `v1.0.0`
   - Click **"Publish Release"**
   - RunPod will:
     - Build Docker image (~10-15 min)
     - Run 8 automated tests
     - Publish to marketplace if tests pass

4. **Monitor Build Progress**
   - Check build logs in RunPod console
   - Verify all tests pass
   - Once published, the worker will be available in the Hub

### Option 2: Create Template via API

If you prefer to skip the Hub and use your own template:

```bash
# Create serverless template for whisper-hub
curl -X POST "https://api.runpod.io/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -d '{
    "query": "mutation { saveTemplate(input: {
      name: \"whisper-hub-official\",
      imageName: \"ghcr.io/freshhherb/whisper-hub:v1.0.0\",
      dockerArgs: \"python -u src/handler.py\",
      containerDiskInGb: 20,
      volumeInGb: 0,
      isServerless: true,
      env: [
        {key: \"MODEL\", value: \"base\"},
        {key: \"TEMPERATURE\", value: \"0.0\"},
        {key: \"BEAM_SIZE\", value: \"5\"}
      ]
    }) { id name imageName } }"
  }'
```

**Note:** You'll need to build and push the Docker image to a registry first (Docker Hub or GitHub Container Registry).

---

## 🐳 Building and Publishing Docker Image

### Build locally and push to Docker Hub:

```bash
cd D:\code\github\whisper-hub

# Build the image
docker build -t freshhherb/whisper-hub:v1.0.0 -t freshhherb/whisper-hub:latest .

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push freshhherb/whisper-hub:v1.0.0
docker push freshhherb/whisper-hub:latest
```

### Or use GitHub Container Registry:

```bash
# Build the image
docker build -t ghcr.io/freshhherb/whisper-hub:v1.0.0 -t ghcr.io/freshhherb/whisper-hub:latest .

# Login to GitHub Container Registry
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u FresHHerB --password-stdin

# Push to GHCR
docker push ghcr.io/freshhherb/whisper-hub:v1.0.0
docker push ghcr.io/freshhherb/whisper-hub:latest
```

---

## 🚀 Creating Serverless Endpoint

Once the template is created (via Hub or API), create an endpoint:

### Via RunPod Console:
1. Go to **Serverless** → **Create Endpoint**
2. Select template: `whisper-hub-official`
3. Configure:
   - Name: `whisper-official`
   - Min Workers: `0` (pay-per-use)
   - Max Workers: `3`
   - GPU Types: `AMPERE_16`, `AMPERE_24`
   - Idle Timeout: `30s`
4. Click **Deploy**

### Via API:

```bash
curl -X POST "https://api.runpod.io/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -d '{
    "query": "mutation {
      saveEndpoint(input: {
        name: \"whisper-official\",
        templateId: \"YOUR_TEMPLATE_ID\",
        workersMin: 0,
        workersMax: 3,
        gpuIds: \"AMPERE_16,AMPERE_24\",
        scalerType: \"QUEUE_DELAY\",
        scalerValue: 3
      }) {
        id name templateId
      }
    }"
  }'
```

---

## 🧪 Testing Your Endpoint

```bash
# Replace YOUR_ENDPOINT_ID with actual endpoint ID
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -d '{
    "input": {
      "audio": "https://github.com/openai/whisper/raw/main/tests/jfk.flac",
      "model": "base",
      "language": null,
      "word_timestamps": true
    }
  }'
```

Check job status:
```bash
curl "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY"
```

---

## 📊 Current RunPod Account Status

**User ID:** `user_2vvDyNiL9ZeXlft0wcnS0jXu88N`
**Email:** `faelzim34@gmail.com`

**Existing Templates:**
- `api-gpu-worker` (szh34a80oj) - Your custom worker
- `faster-whisper-v1.0.10` (oh8mkykjy7) - Faster Whisper

**Existing Endpoints:**
- `api-gpu-transcription` (82jjrwujznxwvn) - Using faster-whisper
- `api-gpu-worker` (5drobmqv2ctll8) - Using custom worker

---

## 🔗 Important Links

- **GitHub Repository:** https://github.com/FresHHerB/whisper-hub
- **GitHub Release v1.0.0:** https://github.com/FresHHerB/whisper-hub/releases/tag/v1.0.0
- **RunPod Hub (when published):** https://console.runpod.io/hub/FresHHerB/whisper-hub
- **RunPod Console:** https://console.runpod.io

---

## 📝 Configuration Files Summary

### `.runpod/hub.json`
- Hub metadata and configuration
- 4 preset configurations
- Environment variables schema
- GPU requirements

### `.runpod/tests.json`
- 8 automated test cases
- Model validation tests
- Error handling tests
- Performance benchmarks

### `Dockerfile`
- Base: nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
- PyTorch 2.1.2 with CUDA 11.8
- Pre-cached models: base, medium, turbo
- Final size: ~8-10GB

---

## ⚠️ Important Notes

1. **RunPod Hub Publishing:**
   - Requires manual connection via console (API doesn't support Hub management)
   - Docker image will be built automatically by RunPod
   - Tests will run automatically during build

2. **Alternative Approach:**
   - Build and push Docker image manually to Docker Hub/GHCR
   - Create template via API
   - Deploy endpoint via API or console

3. **Recommended Path:**
   - Use RunPod Hub for public marketplace listing
   - Or use manual Docker + API for private deployment

---

## 🎯 Next Action

**Choose one:**

1. **Connect to RunPod Hub manually** (recommended for public listing):
   - Visit: https://console.runpod.io/hub
   - Add `FresHHerB/whisper-hub` repository
   - Publish v1.0.0 release

2. **Build and deploy privately**:
   - Build Docker image locally
   - Push to Docker Hub/GHCR
   - Create template via API
   - Deploy endpoint

Choose based on whether you want public marketplace listing or private deployment.
