"""Venice AI provider (GLM Heretic)"""
import os
import json
from typing import Optional, Generator
import httpx

VENICE_API_KEY = os.getenv("VENICE_API_KEY", "VENICE_ADMIN_KEY_kPp0358Yc9TYZP4JW7pa9ONz3LRuho_n-95t_qbXt6")
VENICE_BASE_URL = "https://api.venice.ai/api/v1"
DEFAULT_MODEL = "olafangensan-glm-4.7-flash-heretic"


class VeniceProvider:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = httpx.Client(timeout=120.0)
        self.thinking_enabled = True
        self.thinking_effort = "medium"
        self.verbosity = "auto"

    def set_thinking(self, enabled: bool = True, effort: str = "medium"):
        self.thinking_enabled = enabled
        self.thinking_effort = effort

    def set_verbosity(self, level: str):
        self.verbosity = level

    def chat(self, messages: list, tools: list = None, stream: bool = False) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "venice_parameters": {
                "disable_thinking": not self.thinking_enabled,
            },
            "reasoning": {
                "effort": self.thinking_effort if self.thinking_enabled else "none",
            },
            "verbosity": self.verbosity,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        if stream:
            payload["stream"] = True
            return self._stream_chat(payload)

        response = self.client.post(
            f"{VENICE_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {VENICE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Venice API error {response.status_code}: {response.text}")

        return response.json()

    def _stream_chat(self, payload: dict) -> Generator:
        with self.client.stream(
            "POST",
            f"{VENICE_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {VENICE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        ) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    yield json.loads(data)

    def chat_stream(self, messages: list, tools: list = None, on_thinking: callable = None, on_content: callable = None):
        """Streaming chat with callbacks for live display.

        Args:
            messages: Chat messages
            tools: Tool schemas
            on_thinking: Called with thinking text chunks
            on_content: Called with content text chunks

        Returns:
            Final message dict (same format as non-streaming)
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "stream": True,
            "venice_parameters": {
                "disable_thinking": not self.thinking_enabled,
            },
            "reasoning": {
                "effort": self.thinking_effort if self.thinking_enabled else "none",
            },
            "verbosity": self.verbosity,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        # Accumulators
        full_content = ""
        full_thinking = ""
        tool_calls = []
        current_tool_call = None

        with self.client.stream(
            "POST",
            f"{VENICE_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {VENICE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        ) as response:
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})

                # Handle thinking/reasoning content
                if delta.get("reasoning_content"):
                    text = delta["reasoning_content"]
                    full_thinking += text
                    if on_thinking:
                        on_thinking(text)

                # Handle regular content
                if delta.get("content"):
                    text = delta["content"]
                    full_content += text
                    if on_content:
                        on_content(text)

                # Handle tool calls
                if delta.get("tool_calls"):
                    for tc_delta in delta["tool_calls"]:
                        idx = tc_delta.get("index", 0)

                        # Ensure we have enough slots
                        while len(tool_calls) <= idx:
                            tool_calls.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })

                        tc = tool_calls[idx]

                        if tc_delta.get("id"):
                            tc["id"] = tc_delta["id"]
                        if tc_delta.get("function", {}).get("name"):
                            tc["function"]["name"] = tc_delta["function"]["name"]
                        if tc_delta.get("function", {}).get("arguments"):
                            tc["function"]["arguments"] += tc_delta["function"]["arguments"]

        # Build final message
        message = {"role": "assistant", "content": full_content or None}
        if full_thinking:
            message["reasoning_content"] = full_thinking
        if tool_calls and tool_calls[0]["id"]:
            message["tool_calls"] = tool_calls

        return {"choices": [{"message": message}]}
