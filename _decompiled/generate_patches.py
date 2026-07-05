#!/usr/bin/env python3
"""
YOLO Annotation Tool Pro - 全面破解补丁
去除：联网校验、VIP校验、版本强制更新、EULA弹窗
版本改为 9.9.9，所有功能直接可用（完全离线）
"""
PY311 = r"C:\Users\xiaoyao\AppData\Local\Programs\Python\Python311\python.exe"
import os, sys, shutil, subprocess, struct, marshal, zlib

BASE_DIR = r"e:\BaiduNetdiskDownload\YOLO_Annotation_Tool_Pro"
OSRC_DIR = os.path.join(BASE_DIR, "_decompiled", "source")
PAT_DIR  = os.path.join(BASE_DIR, "_decompiled", "patches")
PYC_DIR  = os.path.join(BASE_DIR, "_decompiled", "pyc311")
os.makedirs(PAT_DIR, exist_ok=True)
os.makedirs(PYC_DIR, exist_ok=True)

def compile_py(py_path, pyc_path):
    """Compile a .py file to .pyc using Python 3.11"""
    os.makedirs(os.path.dirname(pyc_path), exist_ok=True)
    r = subprocess.run([PY311, "-c", f"""
import py_compile, sys
py_compile.compile(r"{py_path}", cfile=r"{pyc_path}", doraise=True)
print("OK")
    """], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        print(f"  COMPILE ERROR: {py_path}: {r.stderr[:200]}")

def write_module(rel_path, content):
    """Write a patched module and compile it"""
    py_path = os.path.join(PAT_DIR, rel_path)
    pyc_rel = rel_path[:-3] + ".pyc"
    pyc_path = os.path.join(PYC_DIR, pyc_rel)
    os.makedirs(os.path.dirname(py_path), exist_ok=True)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(content)
    compile_py(py_path, pyc_path)

# ============================================================
# 1. app_config/version.py - Change version to 9.9.9
# ============================================================
write_module("app_config/version.py", '''\
VERSION = "9.9.9"
VERSION_INFO = "v"
FULL_TITLE = "YOLO Annotation Tool Pro v"
FULL_TITLE_ALL = " | Patched"
''')

# ============================================================
# 2. app_services/vip_feature_map.py - Strip VIP keys
# ============================================================
write_module("app_services/vip_feature_map.py", '''\
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
''')

# ============================================================
# 3. app_services/vip_license_service.py - Always return True
# ============================================================
write_module("app_services/vip_license_service.py", '''\
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
''')

# ============================================================
# 4. app_services/startup_auth_worker.py - No network auth
# ============================================================
write_module("app_services/startup_auth_worker.py", '''\
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
''')

# ============================================================
# 5. app_network/fn_net_work.py - Stub all network calls
# ============================================================
write_module("app_network/fn_net_work.py", '''\
"""
FN网络通信（已破解：所有API调用直接返回成功/模拟数据）。
"""
import json, os, random, time, base64, socket, subprocess, sys
import psutil
from urllib.parse import urlparse, parse_qs
import requests
import rsa
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

class FNNetWork:
    """FNNetWork - 模拟版，所有操作直接成功。"""

    def __init__(self):
        self.error_msg = ""
        self.crypto_key_aes = None
        self.app_web = ""
        self.crypto_type = 3
        self.Appid = ""
        self.Token = ""
        self.public_key = ""
        self.anti_capture_enabled = True
        self.capture_processes = ('fiddler', 'wireshark', 'charles', 'burpsuite', 'mitmproxy',
                                  'proxyman', 'packet capture', 'httpcan')
        self.common_proxy_ports = (8080, 8888, 8889, 9090, 9999, 3128, 1080, 7890, 7891, 8001, 8118, 9191)
        self.system_proxy_env = ('HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy')

    def _adjust_key_length(self, key_str, length=24):
        return key_str.encode("utf-8").ljust(length, b'\\x00')[:length]

    def int_config(self, config_json):
        return True

    def _extract_appid_from_url(self, url):
        return None

    def rsa_encrypt(self, data):
        import base64 as b64
        return b64.b64encode(data.encode("utf-8")).decode("utf-8")

    def decrypt_with_public_key(self, ciphertext, public_key_pem):
        return "decrypted"

    def aes_encrypt(self, data, key):
        return base64.b64encode(data.encode("utf-8")).decode("utf-8")

    def aes_decrypt(self, data, key):
        return base64.b64decode(data).decode("utf-8", errors="replace")

    def _show_anti_capture_warning(self, detection_msg):
        pass

    def conmonsend(self, data):
        return {"Status": 10000, "Msg": "破解版模拟成功", "Data": {}}

    def get_token(self):
        return True

    def check_link(self):
        return True

    def GetAppUpDataMsg(self):
        return ""

    def get_err_msg(self):
        return self.error_msg

    def login(self, user, passwd, deviceID, Tab, AppVer):
        return {"Status": 10000, "Msg": "登录成功(破解版)",
                "Data": {"User": "patched_user", "Key": "patched_key", "LoginTime": str(int(time.time()))}}

    def get_app_gong_gao(self):
        return False

    def get_app_public_data(self, name, is_special=False):
        return {"Status": 10000, "Data": json.dumps({name: "patched"})}

    def heart_thread(self, is_exit):
        while not is_exit:
            time.sleep(30)

    def GetSystemTime(self):
        return int(time.time())

    def SetUserConfig(self, name, value):
        return {"Status": 10000, "Msg": "设置成功(破解版)"}

    def GetUserConfig(self, name):
        return {"Status": 10000, "Data": "{}"}

    def get_app_version(self, version, is_version_all):
        return {"Status": 10000,
                "Data": {"NewVersion": "9.9.9", "IsUpdate": False, "Msg": "当前已是最新版本"}}

    def check_user_exists(self, user):
        return True

    def get_user_viportime(self):
        return int(time.time()) + 365*86400*9999

    def login_out(self):
        return True

    def HeartBeat(self):
        return True

    def user_register(self, user, passwd, deviceID, SuperPassWord="", Qq="", Email="", Phone=""):
        return {"Status": 10000, "Msg": "注册成功(破解版)"}
''')

# ============================================================
# 6. app_services/startup_preload.py - Keep as-is
# ============================================================
write_module("app_services/startup_preload.py", '''\
"""
启动阶段主线程预导入重模块，缩短进入主界面后的首屏等待。
"""
def preload_startup_modules():
    import app_main.main_window
    import app_pages.annotation_page
    import app_pages.training_page
    import app_pages.validation_page
    import app_pages.http_service_page
''')

# ============================================================
# 7. app_network/fn_app_config.py - Keep config, update URL
# ============================================================
write_module("app_network/fn_app_config.py", '''\
"""飞鸟验证平台应用配置（已破解）。"""
FN_APP_CONFIG = {
    "AppWeb": "http://localhost/patched",
    "CryptoKeyPublic": "-----BEGIN PUBLIC KEY-----\\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDKtTmvs64OuYlM0OUciz0SsqxZ\\nJXV7lnYQ7Ad7qhT3ta1dguImxhS+inY6mJHEjX3Et8wnUW1LW6XtMoH7T4E17ySG\\ntOPu2VEMGy7uNHXohHK7J42L7/h84hU+llAg5FEzho6Bpm463Zpo4Y5iWCS0WmSD\\nAybv6Y6XGrbsMIzhGwIDAQAB\\n-----END PUBLIC KEY-----\\n",
    "CryptoType": 3,
}
APP_UPDATE_URL = "http://localhost/patched/updates"
''')

# ============================================================
# 8. app_config/catalog_embed.py - Keep original content
# ============================================================
# Copy the original catalog_embed.py since it's just data
with open(os.path.join(OSRC_DIR, "app_config", "catalog_embed.py"), "r", encoding="utf-8") as f:
    catalog_content = f.read()
write_module("app_config/catalog_embed.py", catalog_content)

# ============================================================
# 9. app_services/app_version_store.py - Set version to 9.9.9
# ============================================================
write_module("app_services/app_version_store.py", '''\
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
''')

# ============================================================
# 10. app_services/device_identity_store.py
# ============================================================
write_module("app_services/device_identity_store.py", '''\
"""启动后缓存的设备指纹 MD5（离线版）。"""
_device_md5: str = "PATCHED_DEVICE_OFFLINE"

def set_device_md5(value: str):
    global _device_md5
    _device_md5 = value.strip() or "PATCHED_DEVICE_OFFLINE"

def get_device_md5() -> str:
    return _device_md5
''')

# ============================================================
# 11. app_services/fn_session.py - Stub session
# ============================================================
write_module("app_services/fn_session.py", '''\
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
''')

# ============================================================
# 12. app_main/eula_dialog.py - Skip EULA check
# ============================================================
write_module("app_main/eula_dialog.py", '''\
"""
EULA协议对话框（已破解：自动同意，不弹窗）。
"""
import json, os, time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                                QTextEdit, QVBoxLayout, QWidget)
from app_config.version import VERSION

EULA_VERSION = "0.0.0"
END_USER_LICENSE_AGREEMENT = ""

@dataclass
class EulaState:
    agreed: bool = True
    version: str = ""

def _agreement_file_path() -> Path:
    return Path(os.path.expanduser("~")) / ".yolo_annotator" / "eula_agreement.json"

def load_eula_state() -> EulaState:
    return EulaState(agreed=True, version="patched")

def save_eula_state():
    path = _agreement_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"eula_agreed": True, "timestamp": time.time(),
            "version": "patched", "agreement_type": "EULA"}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class EULADialog(QDialog):
    def __init__(self, eula_text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.eula_text = eula_text
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("最终用户许可协议 (EULA)")
        self.setFixedSize(760, 520)

def ensure_eula_accepted(parent=None):
    """已破解：直接同意，不显示弹窗。"""
    save_eula_state()
    return True
''')

# ============================================================
# 13. main.py - Skip EULA, skip auth checks
# ============================================================
write_module("main.py", """\
import sys

def _bootstrap_http_subcommand():
    \"\"\"打包 HTTP 子进程：须在 PySide6 / SAM3 导入之前退出。\"\"\"
    import __name__
    if __name__ == "__main__":
        from app_services.frozen_runtime import configure_frozen_runtime
        from app_services.ultralytics_fonts import ensure_ultralytics_font_files
        configure_frozen_runtime()
        ensure_ultralytics_font_files()
        if len(sys.argv) >= 2 and sys.argv[1] == '--run-http-server':
            sys.argv.pop(1)
            from app_services.http_server_entry import main as http_main
            http_main()
            raise SystemExit(0)

def main():
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    import app_resource_rc
    import os
    os.environ.setdefault('QT_OPENGL', 'software')

    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon
    import sys
    from app_services.exception_handler import global_exception_handler
    global_exception_handler.install()

    app = QApplication(sys.argv)
    app.setProperty("exceptionHandler", global_exception_handler)
    app.setWindowIcon(QIcon(":/app_resource/images/app.ico"))

    # 跳过EULA
    from app_main.eula_dialog import ensure_eula_accepted
    ensure_eula_accepted()

    # 初始化目录
    from app_services.paths import ensure_app_directories, migrate_legacy_config_files
    ensure_app_directories()
    migrate_legacy_config_files()

    # 启动加载窗口（无网络校验）
    from app_main.loading_window import LoadingWindow
    loading = LoadingWindow()
    loading.start_auth()

    if loading.exec() == loading.DialogCode.Accepted:
        auth_result = loading.auth_result()
        if auth_result and not auth_result.ok:
            from app_widgets.zh_message_box import critical_ok
            detail = auth_result.error_message or ""
            if auth_result.update_message:
                detail += "\\n\\n" + auth_result.update_message
            critical_ok("启动失败", f"\\n{detail}")
            sys.exit(1)

        # 设置版本
        from app_config.version import VERSION
        from app_services.app_version_store import set_startup_versions
        set_startup_versions("9.9.9", "9.9.9")

        # 启动主窗口
        from app_main.main_window import MainWindow
        from app_services.vip_license_service import can_use
        MainWindow.apply_vip_gates()

        window = MainWindow()
        window.set_main_window(global_exception_handler)
        window.show()

        # 第一次启动时提示打开最近项目
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, window.annotation_page.prompt_open_recent_project)
    else:
        sys.exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if sys.platform == "nt":
        import multiprocessing
        multiprocessing.set_start_method("forkserver", force=True)
    main()
""")

# ============================================================
# 14. app_services/paths.py - Keep original
# ============================================================
write_module("app_services/paths.py", open(os.path.join(OSRC_DIR, "app_services", "paths.py"), "r", encoding="utf-8").read())

# ============================================================
# 15. app_services/frozen_runtime.py - Keep original
# ============================================================
write_module("app_services/frozen_runtime.py", open(os.path.join(OSRC_DIR, "app_services", "frozen_runtime.py"), "r", encoding="utf-8").read())

# ============================================================
# 16. app_services/http_server_entry.py - Keep original
# ============================================================
write_module("app_services/http_server_entry.py", open(os.path.join(OSRC_DIR, "app_services", "http_server_entry.py"), "r", encoding="utf-8").read())

# ============================================================
# 17. app_main/main_window.py - Keep original (it calls VIP gates properly)
# ============================================================
write_module("app_main/main_window.py", open(os.path.join(OSRC_DIR, "app_main", "main_window.py"), "r", encoding="utf-8").read())

# ============================================================
# 18. app_main/loading_window.py - Keep original
# ============================================================
write_module("app_main/loading_window.py", open(os.path.join(OSRC_DIR, "app_main", "loading_window.py"), "r", encoding="utf-8").read())

# Print all patched files
print("\\n=== 生成的补丁文件 ===")
for root, dirs, files in os.walk(PAT_DIR):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, PAT_DIR)
            size = os.path.getsize(path)
            print(f"  {rel} ({size} bytes)")

print(f"\\n补丁文件已生成到: {PAT_DIR}")
print(f"编译后的 pyc 文件到: {PYC_DIR}")
