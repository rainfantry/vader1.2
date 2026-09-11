"""Terminal execution tools"""
import subprocess
import re

DANGEROUS_PATTERNS = [
    r"\brm\s+-rf", r"\bdel\s+/[sq]", r"format\s+[a-z]:", r"drop\s+database",
    r"truncate\s+table", r"--force", r"--hard", r"git\s+push.*-f", r"git\s+reset\s+--hard",
]


def is_dangerous(command: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def bash(command: str, timeout: int = 120) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        return output[:10000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


def powershell(command: str, timeout: int = 120) -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        return output[:10000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"
