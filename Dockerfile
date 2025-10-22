# ==================================
# RunPod Serverless Worker: OpenAI Whisper Official
# ==================================
# CUDA 11.8 + PyTorch 2.1.2 + OpenAI Whisper
# Pre-cached models: base, medium, turbo
# Optimized for GPU inference with FP16
#
# Based on: runpod-workers/worker-faster_whisper
# Engine: OpenAI Whisper (PyTorch) instead of faster-whisper (CTranslate2)
# Target size: ~8-10GB (CUDA + PyTorch + models)

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Metadata
LABEL maintainer="whisper-hub-team"
LABEL description="RunPod Serverless Worker - OpenAI Whisper Official"
LABEL version="1.0.0"
LABEL cuda.version="11.8"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set shell to bash
SHELL ["/bin/bash", "-c"]

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    git \
    wget \
    curl \
    # Python 3.10
    python3.10 \
    python3-pip \
    python3.10-dev \
    # FFmpeg for audio processing
    ffmpeg \
    # SSL certificates
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Install PyTorch with CUDA 11.8 support (~4.6GB)
RUN pip install --no-cache-dir \
    torch==2.1.2 \
    torchaudio==2.1.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install OpenAI Whisper with NumPy 1.x (PyTorch 2.1.2 requires NumPy <2)
RUN pip install --no-cache-dir "numpy<2" openai-whisper

# Working directory
WORKDIR /app

# Copy builder requirements and install
COPY builder/requirements.txt /app/builder/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /app/builder/requirements.txt

# Pre-download Whisper models to reduce cold start
# This adds ~4-5GB but eliminates runtime downloads (8min → 30s cold start)
COPY builder/fetch_models.py /app/builder/fetch_models.py
RUN python /app/builder/fetch_models.py && \
    rm -rf /app/builder

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy application source
COPY src/ /app/src/

# Copy test input
COPY test_input.json /app/test_input.json

# Verify installations
RUN python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
RUN python -c "import whisper; print(f'Whisper installed: {whisper.__version__ if hasattr(whisper, \"__version__\") else \"OK\"}')"
RUN python -c "import runpod; print(f'RunPod SDK: {runpod.__version__}')"

# RunPod Serverless entry point
CMD ["python", "-u", "src/handler.py"]
