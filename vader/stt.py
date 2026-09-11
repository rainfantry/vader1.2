"""STT via Windows Speech Recognition"""
import subprocess
import sys
import tempfile
from pathlib import Path


def listen(timeout: int = 10) -> str:
    """Listen for speech and return transcribed text.

    Args:
        timeout: Max seconds to listen (default 10)

    Returns:
        Transcribed text, or empty string on failure/timeout
    """
    if sys.platform != "win32":
        return ""

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
