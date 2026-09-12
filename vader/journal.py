"""Session journal and learnings persistence for VADER"""
import os
import json
from datetime import datetime

VADER_DIR = os.path.dirname(os.path.dirname(__file__))
SESSIONS_DIR = os.path.join(VADER_DIR, "sessions")
LEARNINGS_FILE = os.path.join(VADER_DIR, "learnings.json")


def _ensure_dirs():
    """Create sessions directory if needed."""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def save_session(messages: list, summary: str = None):
    """Save a conversation session to file."""
    _ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{timestamp}.json"
    filepath = os.path.join(SESSIONS_DIR, filename)

    data = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "messages": messages
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename


def list_sessions(limit: int = 10) -> str:
    """List recent sessions."""
    _ensure_dirs()
    files = sorted(os.listdir(SESSIONS_DIR), reverse=True)[:limit]
    if not files:
        return "No sessions saved yet."

    lines = ["Recent sessions:"]
    for f in files:
        filepath = os.path.join(SESSIONS_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                summary = data.get("summary", "")[:50] or "(no summary)"
                ts = data.get("timestamp", "")[:16]
                lines.append(f"  {f}: {ts} - {summary}")
        except:
            lines.append(f"  {f}")
    return "\n".join(lines)


def load_session(filename: str) -> list:
    """Load a session's messages."""
    filepath = os.path.join(SESSIONS_DIR, filename)
    if not os.path.exists(filepath):
        # Try adding .json
        if not filename.endswith(".json"):
            filepath = os.path.join(SESSIONS_DIR, filename + ".json")

    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("messages", [])


# === LEARNINGS SYSTEM ===

def _load_learnings() -> list:
    """Load learnings from file."""
    if os.path.exists(LEARNINGS_FILE):
        try:
            with open(LEARNINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []


def _save_learnings(learnings: list):
    """Save learnings to file."""
    with open(LEARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(learnings, f, indent=2, ensure_ascii=False)


def add_learning(text: str) -> str:
    """Add a learning."""
    learnings = _load_learnings()
    entry = {
        "id": len(learnings) + 1,
        "text": text,
        "added": datetime.now().isoformat()
    }
    learnings.append(entry)
    _save_learnings(learnings)
    return f"Learned #{entry['id']}: {text[:50]}{'...' if len(text) > 50 else ''}"


def list_learnings() -> str:
    """List all learnings."""
    learnings = _load_learnings()
    if not learnings:
        return "No learnings saved. Use /learn <thing> to add."

    lines = ["Learnings:"]
    for l in learnings:
        lines.append(f"  #{l['id']}: {l['text'][:60]}{'...' if len(l['text']) > 60 else ''}")
    return "\n".join(lines)


def forget_learning(id_num: int) -> str:
    """Remove a learning by ID."""
    learnings = _load_learnings()
    original_len = len(learnings)
    learnings = [l for l in learnings if l.get("id") != id_num]

    if len(learnings) == original_len:
        return f"Learning #{id_num} not found."

    _save_learnings(learnings)
    return f"Forgot learning #{id_num}"


def get_learnings_context() -> str:
    """Get learnings as context for LLM."""
    learnings = _load_learnings()
    if not learnings:
        return ""

    lines = ["[VADER Learnings - things to remember:]"]
    for l in learnings:
        lines.append(f"- {l['text']}")
    return "\n".join(lines)
