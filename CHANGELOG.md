# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-22
## [1.0.5] - 2025-01-29

### Fixed
- **Critical:** Removed `tokens` field from segment output to prevent HTTP 400 Bad Request errors
- Issue where job completed successfully but RunPod API rejected the output due to payload size exceeding 10MB limit
- Reduced typical payload size by ~80% (from 15-20MB to 3-4MB for 2-minute audio)

### Changed
- Segment output no longer includes token IDs (not used by orchestrator)
- Updated EXAMPLE_OUTPUT.json to reflect new format

### Technical Details
- RunPod serverless has a 10MB output limit per job
- For a 2-minute audio with 39 segments, the tokens array could contain 50,000+ elements
- This resulted in JSON payloads of 15-20MB, causing RunPod to return HTTP 400
- Worker logs showed "Job completed successfully" but orchestrator received "output is missing"


### Added
- Initial release of OpenAI Whisper Official worker for RunPod
- GPU-optimized transcription (CUDA 11.8, PyTorch 2.1.2)
- Pre-cached models: base, medium, turbo
- FP16 automatic mode for 50% VRAM reduction
- TF32 support on Ampere GPUs for 30% speedup
- Word-level timestamps for karaoke/highlighting
- Automatic language detection
- Thread-safe model loading with caching
- Comprehensive input validation
- Audio download with progress tracking
- Detailed logging and error handling

### Features
- Models: base (74M), medium (769M), turbo (809M)
- Input formats: mp3, wav, m4a, flac, etc.
- Output: segments, word timestamps, detected language, full transcription
- GPU VRAM monitoring
- Automatic cleanup of temporary files

### Performance
- Cold start: ~30s-2min (pre-cached models)
- Warm start: ~10-20s (FlashBoot)
- RTF: 0.025-0.05x (20-40x real-time on RTX 4090)
