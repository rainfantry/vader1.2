"""Browser automation via kimi-webbridge daemon"""
import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

WEBBRIDGE_EXE = Path.home() / ".kimi-webbridge" / "bin" / "kimi-webbridge.exe"
DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "vader-session"


def _call_webbridge(action: str, args: dict, session: str = SESSION_NAME) -> dict:
    """Make a request to webbridge daemon. Returns response dict."""
    payload = {
        "action": action,
        "args": args,
        "session": session
    }

    # Write to temp file (Windows requires this for non-ASCII)
    temp_path = Path(tempfile.gettempdir()) / f"webbridge-req-{uuid.uuid4().hex[:8]}.json"
    temp_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        result = subprocess.run(
            ["curl.exe", "-s", "-X", "POST", DAEMON_URL,
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{temp_path}"],
            capture_output=True,
            timeout=30,
            encoding="utf-8",
            errors="replace"
        )
        temp_path.unlink(missing_ok=True)

        if result.returncode != 0:
            return {"ok": False, "error": {"message": f"curl failed: {result.stderr or 'unknown'}"}}

        stdout = result.stdout or ""
        if not stdout.strip():
            return {"ok": False, "error": {"message": "Empty response from daemon"}}

        return json.loads(stdout)

    except json.JSONDecodeError as e:
        return {"ok": False, "error": {"message": f"Invalid JSON: {e}"}}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"message": "Request timed out"}}
    except Exception as e:
        return {"ok": False, "error": {"message": str(e)}}
    finally:
        temp_path.unlink(missing_ok=True)


def _ensure_daemon() -> bool:
    """Ensure webbridge daemon is running. Returns True if ready."""
    # Check status
    result = subprocess.run(
        [str(WEBBRIDGE_EXE), "status"],
        capture_output=True, text=True, timeout=5
    )
    try:
        status = json.loads(result.stdout)
        if status.get("running"):
            return True
    except:
        pass

    # Start it
    subprocess.run([str(WEBBRIDGE_EXE), "start"], capture_output=True, timeout=10)
    return True


def browser_action(action: str, url: str = None, selector: str = None, text: str = None,
                   direction: str = "down", amount: int = 500, new_tab: bool = False) -> str:
    """Browser automation via webbridge.

    Actions: navigate, click, fill, snapshot, screenshot, evaluate, scroll, close
    """
    if not WEBBRIDGE_EXE.exists():
        return "Error: kimi-webbridge not installed. Install from https://www.kimi.com/en/products/kimi-webbridge"

    try:
        _ensure_daemon()
    except Exception as e:
        return f"Error starting daemon: {e}"

    args = {}

    if action == "navigate":
        if not url:
            return "Error: url required for navigate"
        args = {"url": url, "newTab": new_tab, "group_title": "VADER Browser"}
        resp = _call_webbridge("navigate", args)
        if resp.get("ok"):
            data = resp.get("data", {})
            return f"Navigated to {data.get('url')} (tab {data.get('tabId')})"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "scroll":
        # Scroll via JavaScript
        if direction == "up":
            code = f"window.scrollBy(0, -{amount})"
        elif direction == "down":
            code = f"window.scrollBy(0, {amount})"
        elif direction == "top":
            code = "window.scrollTo(0, 0)"
        elif direction == "bottom":
            code = "window.scrollTo(0, document.body.scrollHeight)"
        else:
            code = f"window.scrollBy(0, {amount})"
        resp = _call_webbridge("evaluate", {"code": code})
        if resp.get("ok"):
            return f"Scrolled {direction} by {amount}px"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "click":
        if not selector:
            return "Error: selector required for click"
        resp = _call_webbridge("click", {"selector": selector})
        if resp.get("ok"):
            data = resp.get("data", {})
            return f"Clicked {data.get('tag', 'element')}: {data.get('text', '')[:50]}"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "fill" or action == "type":
        if not selector or text is None:
            return "Error: selector and text required for fill"
        resp = _call_webbridge("fill", {"selector": selector, "value": text})
        if resp.get("ok"):
            return f"Filled {selector} with text"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "snapshot" or action == "read":
        resp = _call_webbridge("snapshot", {})
        if resp.get("ok"):
            data = resp.get("data", {})
            tree = data.get("tree", "")
            title = data.get("title", "")
            url = data.get("url", "")
            return f"Page: {title}\nURL: {url}\n\nContent:\n{tree[:5000]}"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "screenshot":
        resp = _call_webbridge("screenshot", {"format": "png"})
        if resp.get("ok"):
            data = resp.get("data", {})
            return f"Screenshot saved to: {data.get('path')}"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "evaluate" or action == "js":
        if not text:
            return "Error: code required for evaluate (pass in text arg)"
        resp = _call_webbridge("evaluate", {"code": text})
        if resp.get("ok"):
            data = resp.get("data", {})
            return f"Result ({data.get('type')}): {json.dumps(data.get('value'))}"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    elif action == "close":
        resp = _call_webbridge("close_session", {})
        if resp.get("ok"):
            return f"Closed {resp.get('data', {}).get('closed', 0)} tabs"
        return f"Error: {resp.get('error', {}).get('message', 'Unknown error')}"

    else:
        return f"Unknown action: {action}. Use: navigate, click, fill, snapshot, screenshot, evaluate, close"
