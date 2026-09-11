# VADER Unified

Dual-brain terminal agent - Venice (GLM Heretic) + Claude.

## Features

- **Venice primary** - Fast, cheap, GLM Heretic 4.7 with live streaming
- **Claude fallback** - Via CLI subprocess (uses your subscription)
- **Live streaming** - Thinking and content stream token by token
- **Live tool output** - Commands show output line by line as they run (PowerShell on Windows)
- **TTS** - Windows SAPI text-to-speech on responses
- **STT** - Whisper (faster-whisper) offline voice input with auto-listen mode
- **Browser automation** - Via kimi-webbridge (navigate, click, fill, screenshot, read)
- **Shared memory** - Uses Claude Code memory folder
- **Status bar** - Provider, thinking, TTS, STT, Claude usage (session%/week%), bypass mode
- **History** - ↑↓ arrows for command history, Tab for autocomplete

## Usage

```bash
# Interactive mode
vader

# Or directly
python vader.py
```

## Commands

| Command | Action |
|---------|--------|
| `/help` | Show commands |
| `/model <v\|c>` | Switch Venice/Claude |
| `/usage` | Claude subscription usage |
| `/thinking <on\|off\|effort>` | Thinking mode (none/minimal/low/medium/high/xhigh/max) |
| `/verbose <low\|med\|high>` | Response verbosity |
| `/bypass` | Toggle dangerous cmd skip (RED status bar) |
| `/tts <on\|off\|test>` | Text-to-speech output |
| `/stt <on\|off\|test\|devices>` | Speech-to-text (Whisper offline) |
| `@` | Trigger voice input (when stt enabled) |
| `/memory list\|read <name>` | Memory ops |
| `/reset` | Clear context |
| `/status` | Show all states |

**Keyboard shortcuts:** `↑↓` command history, `Tab` autocomplete commands and args

## Live Streaming

Responses stream live:
- **Thinking** - Shows `[thinking]` prefix with reasoning tokens
- **Content** - Appears word by word
- **Tool output** - Bash commands show `│ line` for each output line

## Voice

```
/tts on       # Speak responses aloud (Windows SAPI)
/stt on       # Voice mode - auto-listens after each response
/stt off      # Back to keyboard only
/stt test     # Test microphone
/stt devices  # List audio input devices
```

Voice mode is continuous - after each response, it listens again. Ctrl+C exits to keyboard.
Status bar shows `stt:@` when enabled. TTS strips markdown and truncates long responses (400 char limit).

**Natural language control:** Say "turn on speech" or "enable TTS" and the LLM uses slash commands internally.

## Browser Automation

Requires kimi-webbridge extension connected. The agent can:
- Navigate to URLs (reuses same tab by default)
- Scroll up/down/top/bottom like a human
- Click elements (using @e refs from snapshot)
- Fill forms
- Take screenshots
- Read page content (accessibility tree)

## Venice API Params

- `venice_parameters.disable_thinking: true/false`
- `reasoning.effort: none/minimal/low/medium/high/xhigh/max`
- `verbosity: low/medium/high/auto`

## Architecture

```
vader/
├── core.py             # Main agent loop with streaming
├── providers/
│   ├── venice.py       # Venice API with streaming
│   └── claude.py       # Claude CLI subprocess
├── tools/
│   ├── terminal.py     # bash/powershell with live output
│   ├── files.py        # read/write/glob/grep
│   ├── memory.py       # shared memory
│   └── browser.py      # kimi-webbridge
├── commands/           # Slash commands
├── tts.py              # Windows SAPI TTS
└── stt.py              # faster-whisper STT (offline)
```

## Requirements

- Python 3.10+
- Windows (for TTS - uses SAPI)
- httpx
- prompt_toolkit (autocomplete, history)
- faster-whisper (offline STT)
- sounddevice, numpy (voice activity detection)
- Claude CLI (for /usage and Claude provider)
- kimi-webbridge Chrome extension (optional, for browser)

```bash
pip install -r requirements.txt
```

## Author

George Wu / 22nd Survey Division
