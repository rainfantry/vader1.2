# VADER Unified

Dual-brain terminal agent - Venice (GLM Heretic) + Claude.

## Features

- **Venice primary** - Fast, cheap, GLM Heretic 4.7
- **Claude fallback** - Via CLI subprocess (uses your subscription)
- **Tool execution** - bash, file ops, grep, glob
- **Shared memory** - Uses Claude Code memory folder
- **Status bar** - Provider, thinking, TTS, bypass mode
- **Slash commands** - Model switching, settings, memory

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
| `/thinking <on\|off\|effort>` | Thinking mode |
| `/verbose <low\|med\|high>` | Response length |
| `/bypass` | Toggle dangerous cmd skip (RED status) |
| `/tts <on\|off>` | Speech output |
| `/memory list\|read <name>` | Memory ops |
| `/reset` | Clear context |
| `/status` | Show all states |

## Venice API Params

- `venice_parameters.disable_thinking: true/false`
- `reasoning.effort: none/minimal/low/medium/high/xhigh/max`
- `verbosity: low/medium/high/auto`

## Architecture

```
vader/
├── providers/
│   ├── venice.py      # Venice API (primary)
│   └── claude.py      # Claude CLI subprocess
├── tools/
│   ├── terminal.py    # bash/powershell
│   ├── files.py       # read/write/glob/grep
│   ├── memory.py      # shared memory
│   └── browser.py     # kimi-webbridge (TODO)
├── commands/          # Slash commands
└── core.py            # Main agent loop
```

## Author

George Wu / 22nd Survey Division
