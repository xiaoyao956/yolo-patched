"""
VIP许可证服务（已破解：所有功能均可使用）。
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from PySide6.QtWidgets import QWidget

_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
_NEW_USER_TRIAL_DAYS = 9999
VIP_DENY_MESSAGE = ""
_DEFAULT_DENY_REASON = ""

@dataclass
class FeatureGrantView:
    enabled: bool = True
    expires_at: Optional[datetime] = None
    reason: str = ""

class VipLicenseStore:
    def __init__(self):
        self._raw: Any = None
        self._features: Dict[str, Any] = {}

    def load_from_vip_info(self, vip_info: Any):
        pass

    @property
    def features(self) -> Dict[str, Any]:
        return {}

    @property
    def heartbeat_exit_on_fail(self) -> bool:
        return False

    def resolve_feature_key(self, name: str) -> Optional[str]:
        return name

    def grant(self, feature_name: str) -> FeatureGrantView:
        return FeatureGrantView(enabled=True)

    def can_use(self, feature_name: str, now: Optional[datetime] = None) -> bool:
        return True

    def reason(self, feature_name: str) -> str:
        return ""

    def check(self, feature_name: str, now: Optional[datetime] = None) -> "FeatureCheckResult":
        return FeatureCheckResult(ok=True, reason="")

@dataclass
class FeatureCheckResult:
    ok: bool = True
    reason: str = ""

_store: Optional[VipLicenseStore] = None

def get_vip_store() -> Optional[VipLicenseStore]:
    global _store
    if _store is None:
        _store = VipLicenseStore()
    return _store

def set_vip_info(vip_info: Any):
    store = VipLicenseStore()
    global _store
    _store = store

def can_use(feature_name: str) -> bool:
    return True

def require_feature(feature_name: str, parent: Optional[QWidget] = None,
                    title: str = "无权限", warning_ok: bool = True) -> bool:
    return True

def build_default_new_user_vip(trial_days: int = 9999, base_time: Optional[datetime] = None) -> Dict[str, Any]:
    return {
        "功能": {
            k: {"启用": True, "到期时间": (datetime.now() + timedelta(days=9999)).strftime(_DATETIME_FMT)}
            for k in ["矩形标注", "多边形标注", "分类标注", "姿态标注", "旋转框OBB",
                      "标注匹配", "SAM模型", "http_server", "http服务",
                      "懒人精灵NCNN", "按键精灵NCNN", "autogo_ncnn", "大漠ONNX"]
        },
        "是否心跳检测结束": False,
    }

def parse_vip_info_string(raw: Any) -> Optional[Dict[str, Any]]:
    return build_default_new_user_vip()

def _parse_vip_root(vip_info: Any) -> Optional[Dict[str, Any]]:
    return build_default_new_user_vip()

def _parse_expires(value: Any) -> Optional[datetime]:
    return datetime.now() + timedelta(days=9999)
