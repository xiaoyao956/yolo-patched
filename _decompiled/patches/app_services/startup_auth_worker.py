"""
启动校验后台线程（已破解：直接成功，不连网络）。
"""
from __future__ import annotations
import json, threading
from dataclasses import dataclass
from typing import Optional
from PySide6.QtCore import QThread, Signal

from app_config.version import VERSION
from app_network.devicesID import get_hardware_identifier, get_sorted_hardware_md5
from app_services.device_identity_store import set_device_md5

@dataclass
class StartupAuthResult:
    ok: bool = True
    error_message: str = ""
    announcement: Optional[str] = None
    update_message: Optional[str] = None
    current_version: str = "9.9.9"
    latest_version: str = "9.9.9"

class StartupAuthWorker(QThread):
    step_changed = Signal(str)
    version_info_changed = Signal(str, str)
    finished = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fn = None
        self._heartbeat_exit = False

    def run(self):
        try:
            result = self._run_pipeline()
        except Exception as exc:
            result = StartupAuthResult(ok=False, error_message=f"启动校验异常：{exc}")
        self.finished.emit(result)

    def start_heartbeat(self):
        pass

    def _emit_step(self, text: str):
        self.step_changed.emit(text)

    def _fail(self, message: str) -> StartupAuthResult:
        return StartupAuthResult(ok=False, error_message=message)

    def _run_pipeline(self) -> StartupAuthResult:
        """完全离线启动：跳过所有网络操作，直接返回成功。"""
        self._emit_step("正在初始化配置中")

        # 生成设备指纹（离线）
        hardware_info = get_hardware_identifier()
        md5_result = get_sorted_hardware_md5(hardware_info)
        if isinstance(md5_result, tuple):
            device_md5 = md5_result[0]
        else:
            device_md5 = md5_result
        set_device_md5(device_md5)

        # 设置版本
        from app_services.app_version_store import set_startup_versions
        set_startup_versions("9.9.9", "9.9.9")

        # 设置VIP（全部可用）
        from app_services.vip_license_service import build_default_new_user_vip, set_vip_info
        vip_info = build_default_new_user_vip()
        set_vip_info(vip_info)

        self._emit_step("正在加载模块与资源")
        return StartupAuthResult(ok=True, current_version="9.9.9", latest_version="9.9.9")
