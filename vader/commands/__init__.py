"""Slash commands"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import VaderAgent

COMMANDS = {}


def command(name: str):
    def decorator(fn):
        COMMANDS[name] = fn
        return fn
    return decorator


@command("help")
def cmd_help(agent: "VaderAgent", args: str = "") -> str:
    return """
/model <v|c>       - Switch Venice/Claude
/usage             - Claude subscription usage
/thinking <on|off|effort> - Thinking mode
/verbose <low|med|high>   - Response length
/bypass            - Toggle dangerous cmd skip
/tts <on|off|test> - Text-to-speech output
/stt <on|off|test|devices|correct|list> - STT with learnable corrections
/memory list|read <name>  - Claude Code memory (read-only)
/learn <thing>     - Save a learning (persists)
/forget <id>       - Remove a learning
/learnings         - List all learnings
/journal list|save - Session history
/reset             - Clear context
/status            - Show all states

@ + Enter = voice input (when stt on)
↑↓ = history  |  Tab = autocomplete
""".strip()


@command("model")
def cmd_model(agent: "VaderAgent", args: str = "") -> str:
    args = args.strip().lower()
    if args in ("v", "venice"):
        agent.current_provider = "venice"
        return "Switched to Venice (GLM Heretic)"
    elif args in ("c", "claude"):
        agent.current_provider = "claude"
        return "Switched to Claude"
    else:
        return f"Current: {agent.current_provider}. Use /model v or /model c"


@command("usage")
def cmd_usage(agent: "VaderAgent", args: str = "") -> str:
    return agent.claude.usage()


@command("thinking")
def cmd_thinking(agent: "VaderAgent", args: str = "") -> str:
    args = args.strip().lower()
    if args == "on":
        agent.venice.set_thinking(True)
        return "Thinking enabled"
    elif args == "off":
        agent.venice.set_thinking(False)
        return "Thinking disabled"
    elif args in ("none", "minimal", "low", "medium", "high", "xhigh", "max"):
        agent.venice.set_thinking(True, args)
        return f"Thinking effort: {args}"
    else:
        status = "on" if agent.venice.thinking_enabled else "off"
        return f"Thinking: {status}, effort: {agent.venice.thinking_effort}"


@command("verbose")
def cmd_verbose(agent: "VaderAgent", args: str = "") -> str:
    args = args.strip().lower()
    if args in ("low", "med", "medium", "high", "auto"):
        if args == "med":
            args = "medium"
        agent.venice.set_verbosity(args)
        return f"Verbosity: {args}"
    return f"Current verbosity: {agent.venice.verbosity}"


@command("bypass")
def cmd_bypass(agent: "VaderAgent", args: str = "") -> str:
    agent.bypass_enabled = not agent.bypass_enabled
    status = "ON (DANGEROUS)" if agent.bypass_enabled else "OFF"
    return f"Bypass mode: {status}"


@command("tts")
def cmd_tts(agent: "VaderAgent", args: str = "") -> str:
    from ..tts import speak_async
    args = args.strip().lower()
    if args == "on":
        agent.tts_enabled = True
        speak_async("Text to speech enabled")
        return "TTS enabled"
    elif args == "off":
        agent.tts_enabled = False
        return "TTS disabled"
    elif args == "test":
        speak_async("Testing text to speech output")
        return "TTS test sent"
    return f"TTS: {'on' if agent.tts_enabled else 'off'}. Use /tts test to test."


@command("stt")
def cmd_stt(agent: "VaderAgent", args: str = "") -> str:
    from ..stt import is_available, listen, get_devices, add_correction, remove_correction, list_corrections
    parts = args.strip().split(maxsplit=2)
    subcmd = parts[0].lower() if parts else ""

    if subcmd == "on":
        if not is_available():
            return "STT unavailable - install faster-whisper"
        agent.stt_enabled = True
        agent.voice_mode = True
        return "STT enabled - voice mode active"
    elif subcmd == "off":
        agent.stt_enabled = False
        agent.voice_mode = False
        return "STT disabled"
    elif subcmd == "test":
        if not is_available():
            return "STT unavailable - install faster-whisper"
        print("Speak now (records until silence)...")
        text = listen(timeout=10)
        return f"Heard: '{text}'" if text else "No speech detected"
    elif subcmd == "devices":
        devices = get_devices()
        return "Input devices:\n" + "\n".join(devices) if devices else "No devices found"
    elif subcmd == "correct":
        if len(parts) < 3:
            return "Usage: /stt correct <wrong> <right>\nExample: /stt correct 22drv 22DIV"
        wrong = parts[1].strip('"\'')
        right = parts[2].strip('"\'')
        return add_correction(wrong, right)
    elif subcmd == "uncorrect" or subcmd == "remove":
        if len(parts) < 2:
            return "Usage: /stt uncorrect <wrong>"
        wrong = parts[1].strip('"\'')
        return remove_correction(wrong)
    elif subcmd == "list":
        return list_corrections()
    elif not subcmd:
        status = "on" if agent.stt_enabled else "off"
        avail = "Whisper" if is_available() else "unavailable"
        return f"STT: {status} ({avail})\n/stt test | devices | correct <wrong> <right> | list"
    else:
        return f"Unknown: /stt {subcmd}. Try /stt for help."


@command("memory")
def cmd_memory(agent: "VaderAgent", args: str = "") -> str:
    from ..tools.memory import memory_read, memory_list
    parts = args.strip().split(maxsplit=1)
    if not parts:
        return memory_list()
    subcmd = parts[0].lower()
    if subcmd == "list":
        return memory_list()
    elif subcmd == "read" and len(parts) > 1:
        return memory_read(parts[1])
    return "Usage: /memory list | /memory read <name>"


@command("reset")
def cmd_reset(agent: "VaderAgent", args: str = "") -> str:
    agent.messages = []
    return "Context cleared"


@command("status")
def cmd_status(agent: "VaderAgent", args: str = "") -> str:
    thinking = "on" if agent.venice.thinking_enabled else "off"
    bypass = "ON" if agent.bypass_enabled else "off"
    tts = "on" if agent.tts_enabled else "off"
    stt = "on" if agent.stt_enabled else "off"
    return f"""
Provider: {agent.current_provider}
Thinking: {thinking} ({agent.venice.thinking_effort})
Verbosity: {agent.venice.verbosity}
Bypass: {bypass}
TTS: {tts}
STT: {stt}
""".strip()


@command("learn")
def cmd_learn(agent: "VaderAgent", args: str = "") -> str:
    """Save a learning that persists across sessions."""
    from ..journal import add_learning
    if not args.strip():
        return "Usage: /learn <thing to remember>"
    return add_learning(args.strip())


@command("forget")
def cmd_forget(agent: "VaderAgent", args: str = "") -> str:
    """Remove a learning by ID."""
    from ..journal import forget_learning
    try:
        id_num = int(args.strip())
        return forget_learning(id_num)
    except ValueError:
        return "Usage: /forget <id number>"


@command("learnings")
def cmd_learnings(agent: "VaderAgent", args: str = "") -> str:
    """List all saved learnings."""
    from ..journal import list_learnings
    return list_learnings()


@command("journal")
def cmd_journal(agent: "VaderAgent", args: str = "") -> str:
    """Session journal operations."""
    from ..journal import save_session, list_sessions, load_session
    parts = args.strip().split(maxsplit=1)
    subcmd = parts[0].lower() if parts else "list"

    if subcmd == "list":
        return list_sessions()
    elif subcmd == "save":
        summary = parts[1] if len(parts) > 1 else None
        filename = save_session(agent.messages, summary)
        return f"Session saved: {filename}"
    elif subcmd == "load" and len(parts) > 1:
        msgs = load_session(parts[1])
        if msgs:
            agent.messages = msgs
            return f"Loaded {len(msgs)} messages from {parts[1]}"
        return f"Session not found: {parts[1]}"
    return "Usage: /journal list | save [summary] | load <filename>"
