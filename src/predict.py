"""
OpenAI Whisper Predictor for RunPod Serverless.

This module implements the Predictor class that manages Whisper model loading
and transcription processing with GPU optimization.
"""

import os
import threading
from typing import Dict, List, Any, Optional
import torch
import whisper


class Predictor:
    """
    Manages OpenAI Whisper model lifecycle and transcription processing.

    Features:
    - Lazy model loading (load on first use)
    - Thread-safe model management
    - GPU optimization (FP16, TF32 on Ampere)
    - Model caching (one model at a time)
    """

    def __init__(self):
        """Initialize predictor with empty model cache."""
        self.model = None
        self.current_model_name = None
        self.lock = threading.Lock()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Enable GPU optimizations
        if self.device == "cuda":
            # Log GPU info
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"✅ GPU detected: {gpu_name} ({gpu_memory_gb:.1f} GB VRAM)")

            # Enable TF32 on Ampere GPUs (RTX 30xx, A100) for 30% speedup
            if torch.cuda.get_device_capability()[0] >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                print("✅ TF32 enabled (Ampere GPU detected)")
        else:
            print("⚠️ No GPU detected, using CPU")

    def setup(self):
        """
        Setup method called during worker initialization.
        No-op for lazy loading approach.
        """
        print("🔧 Predictor setup complete (lazy loading enabled)")

    def load_model(self, model_name: str) -> whisper.Whisper:
        """
        Load Whisper model with thread-safe caching.

        Args:
            model_name: Name of the model (e.g., 'base', 'medium', 'turbo')

        Returns:
            Loaded Whisper model

        Thread-safe: Yes (uses lock)
        """
        with self.lock:
            # Return cached model if already loaded
            if self.model is not None and self.current_model_name == model_name:
                print(f"♻️ Using cached model: {model_name}")
                return self.model

            # Unload previous model if different
            if self.model is not None and self.current_model_name != model_name:
                print(f"🗑️ Unloading model: {self.current_model_name}")
                del self.model
                if self.device == "cuda":
                    torch.cuda.empty_cache()

            # Load new model
            print(f"📥 Loading model: {model_name} on {self.device}")
            start_time = torch.cuda.Event(enable_timing=True) if self.device == "cuda" else None
            end_time = torch.cuda.Event(enable_timing=True) if self.device == "cuda" else None

            if start_time:
                start_time.record()

            self.model = whisper.load_model(model_name, device=self.device)
            self.current_model_name = model_name

            if end_time:
                end_time.record()
                torch.cuda.synchronize()
                load_time = start_time.elapsed_time(end_time) / 1000  # Convert to seconds

                # Log VRAM usage
                if self.device == "cuda":
                    vram_used_gb = torch.cuda.memory_allocated() / (1024**3)
                    print(f"✅ Model loaded in {load_time:.2f}s ({vram_used_gb:.2f}GB VRAM used)")
            else:
                print(f"✅ Model '{model_name}' loaded successfully")

            return self.model

    def predict(
        self,
        audio_path: str,
        model: str = "base",
        language: Optional[str] = None,
        temperature: float = 0.0,
        beam_size: int = 5,
        word_timestamps: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper.

        Args:
            audio_path: Path to audio file
            model: Model name (base, medium, turbo, etc.)
            language: Language code (e.g., 'pt', 'en') or None for auto-detect
            temperature: Sampling temperature (0.0-1.0)
            beam_size: Beam search size (1-10)
            word_timestamps: Enable word-level timestamps
            **kwargs: Additional whisper.transcribe() parameters

        Returns:
            Dictionary with transcription results:
            {
                "segments": [...],
                "word_timestamps": [...] (if enabled),
                "detected_language": "pt",
                "transcription": "full text...",
                "device": "cuda",
                "model": "base"
            }
        """
        # Load model (cached if same as previous)
        whisper_model = self.load_model(model)

        # Prepare transcription options
        transcribe_options = {
            "language": language,
            "temperature": temperature,
            "beam_size": beam_size,
            "word_timestamps": word_timestamps,
            "verbose": False,
            "fp16": self.device == "cuda",  # Use FP16 on GPU for 50% VRAM savings
        }

        # Remove None values
        transcribe_options = {k: v for k, v in transcribe_options.items() if v is not None}

        print(f"🎤 Starting transcription: model={model}, language={language or 'auto'}, device={self.device}")

        # Log VRAM before transcription
        if self.device == "cuda":
            vram_before = torch.cuda.memory_allocated() / (1024**3)
            print(f"🎮 GPU VRAM before transcription: {vram_before:.2f}GB")

        # Transcribe
        result = whisper_model.transcribe(str(audio_path), **transcribe_options)

        # Log VRAM after transcription
        if self.device == "cuda":
            vram_after = torch.cuda.memory_allocated() / (1024**3)
            print(f"🎮 GPU VRAM after transcription: {vram_after:.2f}GB")
            print(f"✅ Transcription complete")

        # Extract word timestamps if enabled
        word_timestamps_list = []
        if word_timestamps and "segments" in result:
            for segment in result["segments"]:
                if "words" in segment:
                    for word_data in segment["words"]:
                        word_timestamps_list.append({
                            "word": word_data.get("word", "").strip(),
                            "start": word_data.get("start", 0.0),
                            "end": word_data.get("end", 0.0)
                        })

        # Build output
        output = {
            "segments": [
                {
                    "id": seg.get("id", i),
                    "seek": seg.get("seek", 0),
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0),
                    "text": seg.get("text", "").strip(),
                    "temperature": seg.get("temperature", temperature),
                    "avg_logprob": seg.get("avg_logprob", 0.0),
                    "compression_ratio": seg.get("compression_ratio", 0.0),
                    "no_speech_prob": seg.get("no_speech_prob", 0.0),
                }
                for i, seg in enumerate(result.get("segments", []))
            ],
            "detected_language": result.get("language", "unknown"),
            "transcription": result.get("text", "").strip(),
            "device": self.device,
            "model": model,
        }

        # Add word timestamps if generated
        if word_timestamps_list:
            output["word_timestamps"] = word_timestamps_list

        print(f"📊 Transcription stats: {len(output['segments'])} segments, {len(word_timestamps_list)} words")

        return output
