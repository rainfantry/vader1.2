"""VADER's own memory system (separate from Claude Code)"""
import os
from pathlib import Path

# VADER's own memory folder - does NOT touch Claude's memory
VADER_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MEMORY_DIR = VADER_ROOT / "memory"


def memory_read(name: str) -> str:
    mem_file = MEMORY_DIR / f"{name}.md"
    if not mem_file.exists():
        return f"Memory not found: {name}"
    return mem_file.read_text(encoding="utf-8")


def memory_write(name: str, content: str) -> str:
    mem_file = MEMORY_DIR / f"{name}.md"
    mem_file.write_text(content, encoding="utf-8")
    return f"Memory saved: {name}"


def memory_list() -> str:
    if not MEMORY_DIR.exists():
        return "Memory directory not found"
    files = list(MEMORY_DIR.glob("*.md"))
    return "\n".join(f.stem for f in files) or "No memories found"
