"""Claude CLI subprocess provider (uses your subscription)"""
import subprocess
import json
from typing import Optional


class ClaudeProvider:
    def __init__(self, dangerously_skip_permissions: bool = False):
        self.skip_permissions = dangerously_skip_permissions

    def chat(self, prompt: str, print_output: bool = True) -> str:
        cmd = ["claude", "-p", prompt]
        if self.skip_permissions:
            cmd.insert(1, "--dangerously-skip-permissions")

        if print_output:
            cmd.append("--output-format")
            cmd.append("text")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout + result.stderr

    def usage(self) -> str:
        result = subprocess.run(["claude", "/usage"], capture_output=True, text=True, timeout=30)
        return result.stdout

    def is_available(self) -> bool:
        try:
            result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
