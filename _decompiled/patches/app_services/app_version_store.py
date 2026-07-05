"""启动后缓存的应用版本与服务器 NewVersion，供侧栏展示。"""
from app_config.version import VERSION

_current: str = "9.9.9"
_latest: str = "9.9.9"

def normalize_version(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("v"):
        return text[1:]
    return text

def set_startup_versions(current: str, latest: str):
    global _current, _latest
    _current = "9.9.9"
    _latest = "9.9.9"

def get_current_version() -> str:
    return _current

def get_latest_version() -> str:
    return _latest

def has_newer_version() -> bool:
    return False

def format_display_version(version: str) -> str:
    text = version.strip().lower()
    if text.startswith("v"):
        return text
    return "v" + text
