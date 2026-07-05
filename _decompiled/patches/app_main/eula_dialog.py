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
