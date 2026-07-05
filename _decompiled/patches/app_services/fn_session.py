"""FNNetWork 单例（已破解：提供模拟会话）。"""
from __future__ import annotations
from typing import Optional
from app_network.fn_net_work import FNNetWork

_fn: Optional[FNNetWork] = FNNetWork()

def set_fn_client(client: FNNetWork):
    global _fn
    _fn = client

def get_fn_client() -> Optional[FNNetWork]:
    return _fn

def clear_fn_client():
    global _fn
    _fn = None
