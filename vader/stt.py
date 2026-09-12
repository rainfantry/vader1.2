"""STT via faster-whisper (offline, high accuracy) with learnable corrections"""
import sys
import time
import json
import os
import re
import numpy as np

# Try imports
try:
    import sounddevice as sd
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

# Corrections file path
CORRECTIONS_FILE = os.path.join(os.path.dirname(__file__), "stt_corrections.json")

# Config
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 500  # RMS threshold (after *32768 scaling)
SILENCE_DURATION = 1.5   # Seconds of silence to stop recording
MAX_RECORD_SECONDS = 30
WHISPER_MODEL_SIZE = "base"

# Lazy load whisper model
_whisper_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None and HAS_WHISPER:
        print("[stt] Loading Whisper model...", flush=True)
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        print("[stt] Whisper ready.", flush=True)
    return _whisper_model


def record_until_silence(timeout: float = 30) -> np.ndarray:
    """Record audio until silence is detected after speech.

    Returns numpy array of audio or None if no speech.
    """
    if not HAS_WHISPER:
        return None

    audio_chunks = []
    silence_samples = 0
    silence_limit = int(SILENCE_DURATION * SAMPLE_RATE)
    max_samples = int(timeout * SAMPLE_RATE)
    total_samples = 0
    started = False

    def callback(indata, frames, time_info, status):
        nonlocal silence_samples, total_samples, started
        chunk = indata[:, 0].copy()
        rms = np.sqrt(np.mean(chunk ** 2)) * 32768

        if rms > SILENCE_THRESHOLD:
            started = True
            silence_samples = 0
        elif started:
            silence_samples += len(chunk)

        if started:
            audio_chunks.append(chunk)
            total_samples += len(chunk)

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                            dtype="float32", blocksize=1024, callback=callback):
            while True:
                time.sleep(0.05)
                if started and silence_samples >= silence_limit:
                    break
                if total_samples >= max_samples:
                    break
                # Timeout check for pre-speech waiting
                if not started and total_samples == 0:
                    # Check if we've been waiting too long with no speech
                    pass  # Let the max_samples handle this
    except Exception as e:
        print(f"[stt] Recording error: {e}", flush=True)
        return None

    if not audio_chunks:
        return None

    return np.concatenate(audio_chunks)


def transcribe(audio: np.ndarray) -> str:
    """Transcribe audio array to text using Whisper."""
    model = _get_whisper()
    if model is None:
        return ""

    try:
        segments, _ = model.transcribe(audio, beam_size=5, language="en", vad_filter=True)
        text = " ".join(seg.text for seg in segments).strip()
        return text
    except Exception as e:
        print(f"[stt] Transcribe error: {e}", flush=True)
        return ""


def listen(timeout: int = 15, wait_for_speech: bool = True) -> str:
    """Listen for speech and return transcribed text.

    Args:
        timeout: Max seconds to wait/record
        wait_for_speech: Ignored (always waits for speech with this implementation)

    Returns:
        Transcribed text, or empty string if no speech
    """
    if not HAS_WHISPER:
        return ""

    audio = record_until_silence(timeout=timeout)

    if audio is None or len(audio) < SAMPLE_RATE * 0.3:
        return ""

    text = transcribe(audio)
    # Apply learned corrections
    text = apply_corrections(text)
    return text


def is_available() -> bool:
    """Check if faster-whisper STT is available."""
    return HAS_WHISPER


def get_devices():
    """List available audio input devices."""
    if not HAS_WHISPER:
        return []
    try:
        devices = sd.query_devices()
        inputs = []
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                inputs.append(f"{i}: {d['name']}")
        return inputs
    except:
        return []


# === LEARNABLE CORRECTIONS SYSTEM ===

def _load_corrections() -> dict:
    """Load corrections dictionary from file."""
    if os.path.exists(CORRECTIONS_FILE):
        try:
            with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def _save_corrections(corrections: dict):
    """Save corrections dictionary to file."""
    with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(corrections, f, indent=2)


def apply_corrections(text: str) -> str:
    """Apply learned corrections to transcribed text."""
    corrections = _load_corrections()
    if not corrections:
        return text
    result = text
    for wrong, right in corrections.items():
        pattern = re.compile(re.escape(wrong), re.IGNORECASE)
        result = pattern.sub(right, result)
    return result


def add_correction(wrong: str, right: str) -> str:
    """Add a correction mapping. Returns status message."""
    corrections = _load_corrections()
    corrections[wrong.lower()] = right
    _save_corrections(corrections)
    return f"Added: '{wrong}' → '{right}'"


def remove_correction(wrong: str) -> str:
    """Remove a correction mapping. Returns status message."""
    corrections = _load_corrections()
    key = wrong.lower()
    if key in corrections:
        del corrections[key]
        _save_corrections(corrections)
        return f"Removed correction for '{wrong}'"
    return f"No correction found for '{wrong}'"


def list_corrections() -> str:
    """List all corrections."""
    corrections = _load_corrections()
    if not corrections:
        return "No corrections saved."
    lines = [f"  '{k}' → '{v}'" for k, v in corrections.items()]
    return "STT Corrections:\n" + "\n".join(lines)
