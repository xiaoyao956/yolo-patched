"""启动后缓存的设备指纹 MD5（离线版）。"""
_device_md5: str = "PATCHED_DEVICE_OFFLINE"

def set_device_md5(value: str):
    global _device_md5
    _device_md5 = value.strip() or "PATCHED_DEVICE_OFFLINE"

def get_device_md5() -> str:
    return _device_md5
