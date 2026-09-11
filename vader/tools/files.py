"""File operation tools"""
import subprocess
from pathlib import Path


def read_file(path: str, limit: int = 200) -> str:
    p = Path(path)
    if not p.exists():
        return f"File not found: {path}"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(f"{i+1}\t{line}" for i, line in enumerate(lines[:limit]))
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def glob_search(pattern: str, path: str = ".") -> str:
    try:
        base = Path(path)
        matches = list(base.glob(pattern))[:100]
        return "\n".join(str(m) for m in matches) or "No matches"
    except Exception as e:
        return f"Error: {e}"


def grep_search(pattern: str, path: str = ".", glob: str = None) -> str:
    try:
        cmd = f'rg "{pattern}" "{path}"'
        if glob:
            cmd += f' -g "{glob}"'
        cmd += " --max-count=50"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout[:8000] or "No matches"
    except Exception as e:
        return f"Error: {e}"
