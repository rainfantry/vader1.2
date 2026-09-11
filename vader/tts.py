"""TTS via Windows SAPI"""
import subprocess
import sys


def speak(text: str) -> bool:
    """Speak text using Windows SAPI. Returns True on success."""
    if sys.platform != "win32":
        return False

    # Escape quotes for PowerShell
    text = text.replace('"', '`"').replace("'", "''")
    # Limit length for TTS
    if len(text) > 500:
        text = text[:500] + "... truncated"

    ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 2
$synth.Speak("{text}")
'''
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            timeout=30
        )
        return True
    except Exception as e:
        print(f"TTS error: {e}")
        return False


def speak_async(text: str) -> None:
    """Speak text asynchronously (fire and forget)."""
    if sys.platform != "win32":
        return

    # Clean text for TTS - remove special chars that cause issues
    import re
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    text = text.replace('"', '').replace("'", "")
    if len(text) > 500:
        text = text[:500] + " truncated"

    ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 2
$synth.Speak("{text}")
'''
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
    except:
        pass
