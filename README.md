# VADER 1.2

Terminal agent + Web interface with Piper TTS and learnable STT corrections.

## Features

- **Venice AI** - Fast, cheap, GLM Heretic 4.7 with live streaming
- **Piper TTS** - High-quality local neural TTS (no cloud)
- **Whisper STT** - Offline speech-to-text with learnable corrections
- **Gradio Web UI** - Browser interface with voice (works on phone!)
- **Learnings System** - Persistent memory that survives sessions
- **Session Journal** - Auto-save conversations
- **Own Memory** - Separate from Claude Code's memory

## Quick Start

### Terminal Mode
```bash
vader1.2
```

### Web Mode (for phone/browser)
```bash
cd vader1.2
python web.py
```
Open `http://YOUR_PC_IP:7860` on your phone.

## Installation

```bash
# Clone
git clone https://github.com/rainfantry/vader1.2.git
cd vader1.2

# Install dependencies
pip install -r requirements.txt

# Set Venice API key
set VENICE_API_KEY=your_key_here
```

## Commands

| Command | Action |
|---------|--------|
| `/help` | Show all commands |
| `/model <v\|c>` | Switch Venice/Claude |
| `/thinking <on\|off\|effort>` | Thinking mode |
| `/tts <on\|off\|test>` | Text-to-speech (SAPI) |
| `/stt <on\|off\|test>` | Speech-to-text (Whisper) |
| `/stt correct <wrong> <right>` | Teach STT correction |
| `/stt list` | List corrections |
| `/learn <thing>` | Save a learning |
| `/learnings` | Show all learnings |
| `/forget <id>` | Remove a learning |
| `/journal save\|list\|load` | Session management |
| `/memory list\|read` | Read VADER's memory |

## STT Corrections

Whisper mishears things. Teach it:
```
/stt correct 22drv 22DIV
/stt correct spilt22div 22DIV
```

Corrections persist in `vader/stt_corrections.json`.

## Piper TTS

Local neural TTS using Piper. Voice model included: `en_US-lessac-medium`.

### Custom Voice Training

To clone your own voice:
1. Record ~30 min of clean audio
2. Use Piper training scripts (requires GPU)
3. Place `.onnx` model in `voices/` folder

Or use Coqui XTTS (requires Python 3.9-3.11):
- Clones voice with ~10 seconds of audio
- Install: `pip install TTS` (in Python 3.11 venv)

## Web Interface

`web.py` runs a Gradio server:
- Chat with Venice AI
- Shows thinking tokens
- TTS plays in browser (works on phone!)
- Voice input via browser speech API

Access from any device on your network.

## Architecture

```
vader1.2/
├── vader.py            # Terminal entry point
├── web.py              # Gradio web interface
├── vader/
│   ├── core.py         # Main agent loop
│   ├── stt.py          # Whisper + corrections
│   ├── tts.py          # SAPI TTS (terminal)
│   ├── tts_piper.py    # Piper TTS (web)
│   ├── journal.py      # Sessions + learnings
│   ├── providers/      # Venice, Claude
│   ├── tools/          # Files, browser, memory
│   └── commands/       # Slash commands
├── voices/             # Piper voice models
├── memory/             # VADER's own memory
├── sessions/           # Saved conversations
└── learnings.json      # Persistent learnings
```

## Requirements

- Python 3.10+
- Windows (for SAPI TTS in terminal mode)
- See `requirements.txt`

## Author

George Wu / 22nd Survey Division
