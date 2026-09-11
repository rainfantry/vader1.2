"""STT via Windows Speech Recognition with Voice Activity Detection"""
import subprocess
import sys
import time
from pathlib import Path

# Try to import sounddevice for VAD
try:
    import sounddevice as sd
    import numpy as np
    HAS_VAD = True
except ImportError:
    HAS_VAD = False


def wait_for_voice(threshold: float = 0.01, timeout: float = 30, check_interval: float = 0.1) -> bool:
    """Wait until voice is detected (audio level exceeds threshold).

    Args:
        threshold: RMS threshold (0.0-1.0, default 0.01)
        timeout: Max seconds to wait
        check_interval: How often to check audio level

    Returns:
        True if voice detected, False if timeout
    """
    if not HAS_VAD:
        return True  # Skip VAD if no sounddevice

    try:
        start = time.time()
        while time.time() - start < timeout:
            # Record a small chunk
            audio = sd.rec(int(0.1 * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            rms = np.sqrt(np.mean(audio ** 2))
            if rms > threshold:
                return True
            time.sleep(check_interval)
        return False
    except Exception:
        return True  # Fall through to recognition on error


def listen(timeout: int = 10, wait_for_speech: bool = True) -> str:
    """Listen for speech and return transcribed text.

    Args:
        timeout: Max seconds to listen (default 10)
        wait_for_speech: If True, wait for voice activity before recognizing

    Returns:
        Transcribed text, or empty string on failure/timeout
    """
    if sys.platform != "win32":
        return ""

    # Wait for voice activity first
    if wait_for_speech and HAS_VAD:
        if not wait_for_voice(threshold=0.003, timeout=timeout):
            return ""  # No voice detected

    # PowerShell script for speech recognition
    ps_script = f'''
Add-Type -AssemblyName System.Speech
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.SetInputToDefaultAudioDevice()

# Use dictation grammar for free-form speech
$grammar = New-Object System.Speech.Recognition.DictationGrammar
$recognizer.LoadGrammar($grammar)

try {{
    $result = $recognizer.Recognize([TimeSpan]::FromSeconds({timeout}))
    if ($result) {{
        Write-Output $result.Text
    }}
}} catch {{
    Write-Output ""
}} finally {{
    $recognizer.Dispose()
}}
'''

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            encoding="utf-8",
            errors="replace"
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return ""


def listen_continuous(on_result: callable, stop_word: str = "stop listening"):
    """Continuously listen and call on_result with each recognized phrase.

    Stops when stop_word is recognized.

    Args:
        on_result: Called with each transcribed phrase
        stop_word: Phrase that stops listening
    """
    if sys.platform != "win32":
        return

    while True:
        text = listen(timeout=15)
        if text:
            if text.lower().strip() == stop_word.lower():
                break
            on_result(text)


def is_available() -> bool:
    """Check if Windows Speech Recognition is available."""
    if sys.platform != "win32":
        return False

    ps_script = '''
try {
    Add-Type -AssemblyName System.Speech
    $r = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $r.Dispose()
    Write-Output "OK"
} catch {
    Write-Output "FAIL"
}
'''
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == "OK"
    except:
        return False
