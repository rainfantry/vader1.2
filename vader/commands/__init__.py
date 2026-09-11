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
/help              - Show commands
/model <v|c>       - Switch Venice/Claude
/usage             - Claude subscription usage
/thinking <on|off|effort> - Thinking mode
/verbose <low|med|high>   - Response length
/bypass            - Toggle dangerous cmd skip
/tts <on|off>      - Text-to-speech output
/stt <on|off|test> - Speech-to-text input
/memory list|read <name>  - Memory ops
/reset             - Clear context
/status            - Show all states
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
    from ..stt import is_available, listen
    args = args.strip().lower()
    if args == "on":
        if not is_available():
            return "STT unavailable - Windows Speech Recognition not found"
        agent.stt_enabled = True
        return "STT enabled - speak after the 🎤 prompt"
    elif args == "off":
        agent.stt_enabled = False
        return "STT disabled"
    elif args == "test":
        if not is_available():
            return "STT unavailable - Windows Speech Recognition not found"
        print("Listening for 5 seconds...")
        text = listen(timeout=5)
        return f"Heard: '{text}'" if text else "No speech detected"
    status = "on" if agent.stt_enabled else "off"
    avail = "available" if is_available() else "unavailable"
    return f"STT: {status} ({avail}). Use /stt test to test."


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
