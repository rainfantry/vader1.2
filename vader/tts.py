"""TTS via Windows SAPI"""
import subprocess
import sys
import re


def strip_markdown(text: str) -> str:
    """Strip markdown formatting for TTS."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    text = re.sub(r'#{1,6}\s*', '', text)  # headers
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # numbered
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # links
    # Remove emojis and special chars
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def speak(text: str) -> bool:
    """Speak text using Windows SAPI (sync). Returns True on success."""
    if sys.platform != "win32":
        return False

    text = strip_markdown(text)
    if len(text) > 400:
        text = text[:400] + " truncated"

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

    text = strip_markdown(text)
    if len(text) > 400:
        text = text[:400] + " truncated"

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
