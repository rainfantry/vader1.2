# VADER Unified

Dual-brain terminal agent - Venice (GLM Heretic) + Claude.

## Features

- **Venice primary** - Fast, cheap, GLM Heretic 4.7 with live streaming
- **Claude fallback** - Via CLI subprocess (uses your subscription)
- **Live streaming** - Thinking and content stream token by token
- **Live tool output** - Bash commands show output line by line as they run
- **TTS** - Windows SAPI text-to-speech on responses
- **STT** - Windows Speech Recognition for voice input
- **Browser automation** - Via kimi-webbridge (navigate, click, fill, screenshot, read)
- **Shared memory** - Uses Claude Code memory folder
- **Status bar** - Provider, thinking, TTS, STT, bypass mode

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
| `/stt <on\|off\|test>` | Speech-to-text input |
| `/memory list\|read <name>` | Memory ops |
| `/reset` | Clear context |
| `/status` | Show all states |

## Live Streaming

Responses stream live:
- **Thinking** - Shows `[thinking]` prefix with reasoning tokens
- **Content** - Appears word by word
- **Tool output** - Bash commands show `│ line` for each output line

## Voice

```
/tts on       # Speak responses
/stt on       # Voice input (speak after 🎤 prompt)
/stt test     # Test microphone
```

## Browser Automation

Requires kimi-webbridge extension connected. The agent can:
- Navigate to URLs
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
└── stt.py              # Windows Speech Recognition
```

## Requirements

- Python 3.10+
- Windows (for TTS/STT)
- httpx
- Claude CLI (for /usage and Claude provider)
- kimi-webbridge (optional, for browser)

## Author

George Wu / 22nd Survey Division
