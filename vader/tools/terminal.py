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


def bash(command: str, timeout: int = 120, on_output: callable = None) -> str:
    """Execute bash command.

    Args:
        command: Shell command to run
        timeout: Max seconds
        on_output: Optional callback for live output (called with each line)

    Returns:
        Command output
    """
    try:
        if on_output:
            # Live streaming mode
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace"
            )
            output_lines = []
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        output_lines.append(line.rstrip())
                        on_output(line.rstrip())
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return "\n".join(output_lines) + f"\n(timed out after {timeout}s)"
            return "\n".join(output_lines) if output_lines else "(no output)"
        else:
            # Standard mode
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
