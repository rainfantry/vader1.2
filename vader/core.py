"""VADER Core - Main agent loop"""
import os
import sys
import json

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

from .providers import VeniceProvider, ClaudeProvider
from .tools import TOOL_REGISTRY, TOOL_SCHEMAS
from .tools.terminal import is_dangerous
from .commands import COMMANDS
from .tts import speak_async
from .stt import listen, is_available as stt_available

# ANSI colors
GREEN = "\033[38;2;0;255;65m"
AMBER = "\033[38;2;255;176;0m"
RED = "\033[38;2;255;68;68m"
CYAN = "\033[38;2;0;229;255m"
DIM = "\033[38;2;100;100;100m"
RST = "\033[0m"
BOLD = "\033[1m"
BG_RED = "\033[48;2;180;0;0m"


class VaderAgent:
    def __init__(self):
        self.venice = VeniceProvider()
        self.claude = ClaudeProvider()
        self.current_provider = "venice"
        self.messages = []
        self.bypass_enabled = False
        self.tts_enabled = False
        self.stt_enabled = False

    def status_bar(self) -> str:
        provider = self.current_provider[:6]
        thinking = "on" if self.venice.thinking_enabled else "off"
        tts = "on" if self.tts_enabled else "off"
        stt = "on" if self.stt_enabled else "off"

        if self.bypass_enabled:
            bypass = f"{BG_RED}{BOLD}██BYPASS██{RST}"
        else:
            bypass = "BYPASS:OFF"

        return f"{DIM}┌{'─'*70}┐{RST}\n{DIM}│{RST} VADER │ {provider} │ think:{thinking} │ tts:{tts} │ stt:{stt} │ {bypass} {DIM}│{RST}\n{DIM}└{'─'*70}┘{RST}"

    def confirm(self, msg: str) -> bool:
        if self.bypass_enabled:
            return True
        response = input(f"{AMBER}⚠ {msg} [y/N]: {RST}").strip().lower()
        return response in ('y', 'yes')

    def execute_tool(self, name: str, args: dict, live_output: bool = True) -> str:
        print(f"{DIM}[{name}] {json.dumps(args, ensure_ascii=False)[:80]}...{RST}")

        if name == "bash" and is_dangerous(args.get("command", "")):
            if not self.confirm(f"Execute dangerous: {args['command'][:60]}?"):
                return "User rejected dangerous command"

        fn = TOOL_REGISTRY.get(name)
        if not fn:
            return f"Unknown tool: {name}"

        try:
            # Live output for bash commands
            if name == "bash" and live_output:
                def on_line(line):
                    print(f"{DIM}  │ {line}{RST}")
                return fn(on_output=on_line, **args)
            else:
                return fn(**args)
        except Exception as e:
            return f"Error: {e}"

    def chat_venice(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        system = f"""You are VADER, a terminal agent with tool use.
Current directory: {os.getcwd()}
User: George Wu (gwu07)
Be concise. Execute tasks directly."""

        thinking_started = False
        content_started = False

        def on_thinking(text):
            nonlocal thinking_started
            if not thinking_started:
                print(f"{DIM}[thinking] ", end="", flush=True)
                thinking_started = True
            print(f"{DIM}{text}{RST}", end="", flush=True)

        def on_content(text):
            nonlocal content_started, thinking_started
            if thinking_started and not content_started:
                print()  # newline after thinking
            if not content_started:
                print(f"\n", end="")
                content_started = True
            print(text, end="", flush=True)

        while True:
            thinking_started = False
            content_started = False

            response = self.venice.chat_stream(
                [{"role": "system", "content": system}] + self.messages,
                tools=TOOL_SCHEMAS,
                on_thinking=on_thinking,
                on_content=on_content
            )

            msg = response["choices"][0]["message"]

            # Newline after streaming
            if content_started or thinking_started:
                print()

            # Handle tool calls
            if msg.get("tool_calls"):
                self.messages.append(msg)

                for tc in msg["tool_calls"]:
                    fn = tc["function"]
                    args = json.loads(fn["arguments"]) if fn["arguments"] else {}
                    result = self.execute_tool(fn["name"], args)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result
                    })
                    print(f"{DIM}→ {result[:150]}{'...' if len(result)>150 else ''}{RST}")

                continue

            # No tool calls - return response
            content = msg.get("content", "") or ""
            self.messages.append({"role": "assistant", "content": content})
            return content

    def chat_claude(self, user_input: str) -> str:
        return self.claude.chat(user_input)

    def process(self, user_input: str) -> str:
        user_input = user_input.strip()
        if not user_input:
            return ""

        # Handle slash commands
        if user_input.startswith("/"):
            parts = user_input[1:].split(maxsplit=1)
            cmd_name = parts[0].lower()
            cmd_args = parts[1] if len(parts) > 1 else ""

            if cmd_name in COMMANDS:
                return COMMANDS[cmd_name](self, cmd_args)
            else:
                return f"Unknown command: /{cmd_name}. Try /help"

        # Route to provider
        if self.current_provider == "venice":
            return self.chat_venice(user_input)
        else:
            return self.chat_claude(user_input)

    def run(self):
        print(f"{GREEN}╔══════════════════════════════════════════╗{RST}")
        print(f"{GREEN}║  VADER UNIFIED - Venice + Claude Agent   ║{RST}")
        print(f"{GREEN}║  Type /help for commands, exit to quit   ║{RST}")
        print(f"{GREEN}╚══════════════════════════════════════════╝{RST}")
        print(self.status_bar())

        while True:
            try:
                # Voice or text input
                if self.stt_enabled:
                    print(f"\n{CYAN}🎤 Listening...{RST}", end="", flush=True)
                    user_input = listen(timeout=15)
                    if user_input:
                        print(f" {user_input}")
                    else:
                        print(f" (no speech detected)")
                        continue
                else:
                    user_input = input(f"\n{CYAN}>{RST} ").strip()

                if not user_input:
                    continue
                if user_input.lower() == "exit":
                    break

                response = self.process(user_input)
                print(f"\n{response}")

                # TTS output if enabled
                if self.tts_enabled and response and not user_input.startswith("/"):
                    speak_async(response)

                # Update status bar after commands that change state
                if user_input.startswith("/"):
                    print(self.status_bar())

            except KeyboardInterrupt:
                print(f"\n{AMBER}Interrupted{RST}")
                continue
            except EOFError:
                break


def main():
    agent = VaderAgent()
    agent.run()


if __name__ == "__main__":
    main()
