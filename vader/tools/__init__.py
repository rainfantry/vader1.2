from .terminal import bash, powershell
from .files import read_file, write_file, glob_search, grep_search
from .memory import memory_read, memory_write, memory_list
from .browser import browser_action

TOOL_REGISTRY = {
    "bash": bash,
    "powershell": powershell,
    "read_file": read_file,
    "write_file": write_file,
    "glob_search": glob_search,
    "grep_search": grep_search,
    "memory_read": memory_read,
    "memory_write": memory_write,
    "memory_list": memory_list,
    "browser": browser_action,
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {"name": "bash", "description": "Execute bash/shell command", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file contents", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer", "default": 200}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write content to file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "glob_search", "description": "Find files by pattern", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "grep_search", "description": "Search for pattern in files", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."}, "glob": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "memory_read", "description": "Read from memory", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "memory_write", "description": "Write to memory", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "content": {"type": "string"}}, "required": ["name", "content"]}}},
    {"type": "function", "function": {"name": "memory_list", "description": "List all memories", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "browser", "description": "Browser automation via kimi-webbridge", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["navigate", "click", "type", "screenshot", "read"]}, "url": {"type": "string"}, "selector": {"type": "string"}, "text": {"type": "string"}}, "required": ["action"]}}},
]
