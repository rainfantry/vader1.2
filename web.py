"""
VADER 1.2 Web Interface
=======================
Gradio-based chat with:
- Venice AI streaming
- Piper TTS (plays in browser)
- Browser STT (Web Speech API)
- Tool execution display
- Thinking display

Run: python web.py
Open: http://localhost:7860 (or your IP for phone access)
"""

import os
import sys
import json
import base64
import tempfile
from pathlib import Path

# Add vader to path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr

from vader.providers.venice import VeniceProvider
from vader.tts_piper import synthesize, strip_markdown, is_available as piper_available
from vader.stt import apply_corrections

# Initialize Venice
venice = VeniceProvider()
venice.set_thinking(True, "medium")

# Conversation history
messages = []


def chat(user_input: str, history: list):
    """Process chat and stream response."""
    global messages

    if not user_input.strip():
        return history, ""

    # Apply STT corrections
    user_input = apply_corrections(user_input)

    # Add to messages
    messages.append({"role": "user", "content": user_input})

    # Build display history
    history = history or []
    history.append((user_input, ""))

    # Stream response
    full_response = ""
    thinking_text = ""

    def on_thinking(text):
        nonlocal thinking_text
        thinking_text += text

    def on_content(text):
        nonlocal full_response
        full_response += text

    try:
        result = venice.chat_stream(
            messages,
            on_thinking=on_thinking,
            on_content=on_content
        )

        # Get final message
        msg = result["choices"][0]["message"]
        content = msg.get("content", "")
        reasoning = msg.get("reasoning_content", "")

        # Format display
        display = ""
        if reasoning:
            display += f"*[thinking]*\n{reasoning[:500]}{'...' if len(reasoning) > 500 else ''}\n\n"
        display += content

        # Update history
        history[-1] = (user_input, display)

        # Add to messages
        messages.append({"role": "assistant", "content": content})

        return history, ""

    except Exception as e:
        error_msg = f"Error: {e}"
        history[-1] = (user_input, error_msg)
        return history, ""


def text_to_speech(text: str):
    """Generate audio from text using Piper TTS."""
    if not text or not piper_available():
        return None

    # Clean text for TTS
    clean_text = strip_markdown(text)
    if not clean_text:
        return None

    # Limit length
    if len(clean_text) > 500:
        clean_text = clean_text[:500] + "..."

    # Synthesize
    wav_data = synthesize(clean_text)
    if not wav_data:
        return None

    # Save to temp file for Gradio
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(wav_data)
        return f.name


def get_last_response(history):
    """Get last assistant response for TTS."""
    if not history:
        return None
    last = history[-1]
    if len(last) > 1:
        return last[1]
    return None


def speak_last(history):
    """Speak the last response."""
    text = get_last_response(history)
    if text:
        # Remove thinking section
        if "*[thinking]*" in text:
            parts = text.split("\n\n", 1)
            if len(parts) > 1:
                text = parts[1]
        return text_to_speech(text)
    return None


def clear_chat():
    """Clear conversation."""
    global messages
    messages = []
    return [], ""


def get_status():
    """Get system status."""
    status = []
    status.append(f"Venice: {'✓' if venice else '✗'}")
    status.append(f"Piper TTS: {'✓' if piper_available() else '✗'}")
    status.append(f"Messages: {len(messages)}")
    return " | ".join(status)


# Build Gradio interface
with gr.Blocks(title="VADER 1.2") as app:
    gr.Markdown("# VADER 1.2 - Web Interface")
    gr.Markdown("Venice AI + Piper TTS + Browser Speech")

    with gr.Row():
        status = gr.Textbox(value=get_status(), label="Status", interactive=False)

    chatbot = gr.Chatbot(
        label="Chat",
        height=500,
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="Type or use voice input...",
            label="Message",
            scale=4,
            lines=1,
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    with gr.Row():
        speak_btn = gr.Button("🔊 Speak Last Response", scale=1)
        clear_btn = gr.Button("Clear Chat", scale=1)
        audio_out = gr.Audio(label="TTS Output", autoplay=True, visible=True)

    # Voice input using browser API
    with gr.Accordion("Voice Input (Browser Speech API)", open=False):
        gr.Markdown("""
        **Browser Speech Recognition:**
        - Click the microphone icon in your browser's address bar to enable
        - Or use the HTML5 speech input below (Chrome/Edge)

        **On iPhone:**
        - Safari supports voice dictation via keyboard
        - Tap microphone on keyboard to speak
        """)
        voice_input = gr.Textbox(
            placeholder="Speak here... (browser speech input)",
            label="Voice Input",
            elem_id="voice-input"
        )

    # Event handlers
    txt.submit(chat, [txt, chatbot], [chatbot, txt])
    send_btn.click(chat, [txt, chatbot], [chatbot, txt])
    voice_input.submit(chat, [voice_input, chatbot], [chatbot, voice_input])

    speak_btn.click(speak_last, [chatbot], [audio_out])
    clear_btn.click(clear_chat, [], [chatbot, txt])


if __name__ == "__main__":
    import socket

    # Get local IP for phone access
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "localhost"

    print(f"\n╔══════════════════════════════════════════╗")
    print(f"║  VADER 1.2 - Web Interface               ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║  Local:  http://localhost:7860           ║")
    print(f"║  Phone:  http://{local_ip}:7860{''.ljust(20 - len(local_ip))}║")
    print(f"╚══════════════════════════════════════════╝\n")

    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set True for public URL
    )
