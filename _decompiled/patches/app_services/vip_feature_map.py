"""
vipInfo 中文功能键与界面触点的映射。
全部功能已解锁（离线补丁）。
"""
from typing import Dict, FrozenSet

ANNOTATION_MODE_VIP_KEYS: Dict[str, str] = {
    "detect": "矩形标注",
    "segment": "多边形标注",
    "classify": "分类标注",
    "pose": "姿态标注",
    "obb": "旋转框OBB",
}

VIP_KEY_ANNOTATION_MATCH = "标注匹配"
VIP_KEY_SAM = "SAM模型"
VIP_KEY_HTTP_SERVER = "http_server"
VIP_KEY_HTTP_SERVER_CN = "http服务"

EXPORT_ALIAS_VIP_KEYS: Dict[str, str] = {
    "lazy_elf_ncnn": "懒人精灵NCNN",
    "keywizard_ncnn": "按键精灵NCNN",
    "autogo_ncnn": "autogoNCNN",
    "damo_onnx": "大漠ONNX",
}

TRIAL_FEATURE_KEYS: FrozenSet[str] = frozenset(ANNOTATION_MODE_VIP_KEYS.values())
META_HEARTBEAT_EXIT = "是否心跳检测结束"
