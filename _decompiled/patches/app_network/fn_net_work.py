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
        return key_str.encode("utf-8").ljust(length, b'\x00')[:length]

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
