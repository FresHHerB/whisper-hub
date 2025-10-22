"""
Pre-download OpenAI Whisper models during Docker build.

This script downloads specified Whisper models to the default cache directory
(~/.cache/whisper) to eliminate runtime downloads and reduce cold start times.

Models downloaded: base, medium, turbo
Estimated size: ~4-5GB total
Cold start improvement: 8min → 30s-2min
"""

import whisper

def download_model_weights(model_name: str) -> None:
    """
    Download Whisper model weights to cache.

    Args:
        model_name: Name of the model (e.g., 'base', 'medium', 'turbo')
    """
    print(f"📥 Downloading Whisper model: {model_name}")
    try:
        whisper.load_model(model_name)
        print(f"✅ Model '{model_name}' downloaded successfully")
    except Exception as e:
        print(f"❌ Failed to download model '{model_name}': {e}")
        raise


if __name__ == "__main__":
    # Models to pre-download (optimized for balance between quality and size)
    model_names = [
        "base",    # ~140MB, fast, good quality for general use
        "medium",  # ~1.5GB, slower, excellent quality
        "turbo",   # ~1.5GB, fast as base, quality close to large-v3
    ]

    print("=" * 60)
    print("Pre-downloading OpenAI Whisper models for RunPod Hub")
    print("=" * 60)
    print(f"Models to download: {', '.join(model_names)}")
    print()

    for model_name in model_names:
        download_model_weights(model_name)
        print()

    print("=" * 60)
    print("✅ All models pre-downloaded successfully!")
    print("=" * 60)
