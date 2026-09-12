"""Piper TTS - fast, local, natural-sounding text-to-speech"""
import os
import io
import wave
import tempfile
import subprocess
import threading
from pathlib import Path

VADER_ROOT = Path(__file__).parent.parent
VOICES_DIR = VADER_ROOT / "voices"
DEFAULT_VOICE = "en_US-lessac-medium"

# Playback lock
_play_lock = threading.Lock()


def get_voice_path(voice_name: str = None) -> tuple:
    """Get voice model and config paths."""
    voice = voice_name or DEFAULT_VOICE
    model_path = VOICES_DIR / f"{voice}.onnx"
    config_path = VOICES_DIR / f"{voice}.onnx.json"

    if not model_path.exists():
        return None, None
    return str(model_path), str(config_path) if config_path.exists() else None


def synthesize(text: str, voice: str = None) -> bytes:
    """Synthesize text to WAV bytes using Piper."""
    model_path, config_path = get_voice_path(voice)
    if not model_path:
        return None

    try:
        from piper import PiperVoice

        # Load voice
        piper_voice = PiperVoice.load(model_path, config_path)

        # Synthesize to raw audio, then wrap in WAV
        audio_data = b""
        for audio_chunk in piper_voice.synthesize(text):
            audio_data += audio_chunk.audio_int16_bytes

        # Create WAV file
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(piper_voice.config.sample_rate)
            wav_file.writeframes(audio_data)

        return wav_buffer.getvalue()
    except Exception as e:
        print(f"[tts] Piper error: {e}")
        return None


def speak(text: str, voice: str = None, block: bool = True):
    """Speak text using Piper TTS."""
    wav_data = synthesize(text, voice)
    if not wav_data:
        return False

    # Write to temp file and play
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(wav_data)
            temp_path = f.name

        def _play():
            with _play_lock:
                # Use Windows Media Player CLI or PowerShell
                subprocess.run(
                    ["powershell", "-Command",
                     f"(New-Object Media.SoundPlayer '{temp_path}').PlaySync()"],
                    capture_output=True,
                    timeout=30
                )
                try:
                    os.unlink(temp_path)
                except:
                    pass

        if block:
            _play()
        else:
            t = threading.Thread(target=_play, daemon=True)
            t.start()

        return True
    except Exception as e:
        print(f"[tts] Playback error: {e}")
        return False


def speak_async(text: str, voice: str = None):
    """Non-blocking speak."""
    speak(text, voice, block=False)


def list_voices() -> list:
    """List available voice models."""
    if not VOICES_DIR.exists():
        return []
    return [f.stem.replace('.onnx', '') for f in VOICES_DIR.glob("*.onnx")]


def is_available() -> bool:
    """Check if Piper TTS is available."""
    try:
        from piper import PiperVoice
        model_path, _ = get_voice_path()
        return model_path is not None
    except ImportError:
        return False


def strip_markdown(text: str) -> str:
    """Strip markdown for cleaner TTS."""
    import re
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'^[#>*\-]+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[🔊🎤✓✗⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏│├└─═╔╗╚╝║]', '', text)
    return text.strip()
