"""
RunPod Serverless Handler for OpenAI Whisper.

This is the main entry point for the RunPod serverless worker.
It receives audio transcription jobs, processes them using OpenAI Whisper,
and returns transcription results.
"""

import os
import tempfile
import time
from typing import Dict, Any, Optional
import requests
import runpod

# Import predictor
from predict import Predictor


# Initialize predictor (lazy loading)
print("=" * 60)
print("🚀 Initializing OpenAI Whisper Worker")
print("=" * 60)

MODEL = Predictor()
MODEL.setup()

print("=" * 60)
print("✅ Worker ready to process jobs")
print("=" * 60)


def download_audio(url: str, timeout: int = 300) -> str:
    """
    Download audio file from URL to temporary file.

    Args:
        url: Audio file URL
        timeout: Download timeout in seconds

    Returns:
        Path to downloaded temporary file

    Raises:
        Exception: If download fails
    """
    print(f"📥 Downloading audio from: {url}")
    start_time = time.time()

    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Create temporary file
        suffix = os.path.splitext(url)[1] or ".mp3"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
                downloaded += len(chunk)

        temp_file.close()

        download_time = time.time() - start_time
        size_mb = downloaded / (1024 * 1024)
        print(f"✅ Audio downloaded: {size_mb:.2f}MB in {download_time:.2f}s")

        return temp_file.name

    except Exception as e:
        print(f"❌ Failed to download audio: {e}")
        raise Exception(f"Audio download failed: {str(e)}")


def validate_input(job_input: Dict[str, Any]) -> Optional[str]:
    """
    Validate job input parameters.

    Args:
        job_input: Job input dictionary

    Returns:
        Error message if validation fails, None otherwise
    """
    # Check for audio input
    if "audio" not in job_input:
        return "Missing required parameter: 'audio' (URL to audio file)"

    audio_url = job_input.get("audio")
    if not audio_url or not isinstance(audio_url, str):
        return "Invalid 'audio' parameter: must be a non-empty string URL"

    # Validate model if provided
    valid_models = ["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "turbo"]
    model = job_input.get("model", "base")
    if model not in valid_models:
        return f"Invalid model: '{model}'. Valid models: {', '.join(valid_models)}"

    # Validate temperature if provided
    temperature = job_input.get("temperature", 0.0)
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 1:
        return "Invalid temperature: must be between 0 and 1"

    # Validate beam_size if provided
    beam_size = job_input.get("beam_size", 5)
    if not isinstance(beam_size, int) or beam_size < 1 or beam_size > 10:
        return "Invalid beam_size: must be an integer between 1 and 10"

    return None


def run_whisper_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main job handler for Whisper transcription.

    Args:
        job: RunPod job dictionary with 'input' key

    Returns:
        Job output dictionary with transcription results or error

    Job input format:
    {
        "input": {
            "audio": "https://example.com/audio.mp3",
            "model": "base",  # optional
            "language": "pt",  # optional, null for auto-detect
            "temperature": 0.0,  # optional
            "beam_size": 5,  # optional
            "word_timestamps": true  # optional
        }
    }

    Job output format:
    {
        "segments": [...],
        "word_timestamps": [...],  # if word_timestamps=true
        "detected_language": "pt",
        "transcription": "full text...",
        "device": "cuda",
        "model": "base"
    }
    """
    job_input = job.get("input", {})

    print("\n" + "=" * 60)
    print("📋 New transcription job received")
    print("=" * 60)

    # Validate input
    validation_error = validate_input(job_input)
    if validation_error:
        print(f"❌ Validation error: {validation_error}")
        return {"error": validation_error}

    audio_url = job_input["audio"]
    audio_path = None

    try:
        # Download audio
        audio_path = download_audio(audio_url)

        # Extract parameters
        model = job_input.get("model", "base")
        language = job_input.get("language")  # None = auto-detect
        temperature = float(job_input.get("temperature", 0.0))
        beam_size = int(job_input.get("beam_size", 5))
        word_timestamps = bool(job_input.get("word_timestamps", False))

        print(f"📝 Parameters: model={model}, language={language or 'auto'}, "
              f"temperature={temperature}, beam_size={beam_size}, "
              f"word_timestamps={word_timestamps}")

        # Run transcription
        result = MODEL.predict(
            audio_path=audio_path,
            model=model,
            language=language,
            temperature=temperature,
            beam_size=beam_size,
            word_timestamps=word_timestamps
        )

        print("=" * 60)
        print("✅ Job completed successfully")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"❌ Job failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Cleanup temporary audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
                print("🗑️ Temporary audio file cleaned up")
            except Exception as e:
                print(f"⚠️ Failed to cleanup temporary file: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎬 Starting RunPod Serverless Worker")
    print("=" * 60)
    print("Worker: OpenAI Whisper Official")
    print("Models: base, medium, turbo")
    print("Device:", MODEL.device)
    print("=" * 60 + "\n")

    # Start RunPod serverless worker
    runpod.serverless.start({"handler": run_whisper_job})
