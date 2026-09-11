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
