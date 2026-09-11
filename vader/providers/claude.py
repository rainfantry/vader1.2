"""Claude CLI subprocess provider (uses your subscription)"""
import subprocess
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

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,
                encoding="utf-8",
                errors="replace"
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return stdout + stderr
        except subprocess.TimeoutExpired:
            return "Error: Claude CLI timed out after 5 minutes"
        except Exception as e:
            return f"Error: {e}"

    def usage(self) -> str:
        try:
            result = subprocess.run(
                ["claude", "/usage"],
                capture_output=True,
                timeout=30,
                encoding="utf-8",
                errors="replace"
            )
            return result.stdout or ""
        except:
            return ""

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5,
                encoding="utf-8",
                errors="replace"
            )
            return result.returncode == 0
        except:
            return False
