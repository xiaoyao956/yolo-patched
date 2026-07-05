#!/usr/bin/env python3
"""
YOLO Annotation Tool Pro 一键破解补丁
用法：直接双击运行，选择要破解的 exe 即可。
"""
import sys, os, struct, marshal, zlib, shutil, tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

# ---- 内嵌最小 CArchiveReader ----
_MEI_MAGIC = b'MEI\014\013\012\013\016'
_COOKIE_FMT = '!8sIIII64s'
_COOKIE_LEN = struct.calcsize(_COOKIE_FMT)
_ENTRY_FMT = '!IIIIBc'
_ENTRY_HDR_LEN = struct.calcsize(_ENTRY_FMT)

class MiniCArchive:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self._data = f.read()
        cs = self._data.rfind(_MEI_MAGIC)
        if cs < 0:
            raise ValueError("Not a valid PyInstaller archive")
        m, al, to, tl, pv, pln = struct.unpack(
            _COOKIE_FMT, self._data[cs:cs + _COOKIE_LEN])
        self._archive_start = cs + _COOKIE_LEN - al
        self.toc = {}
        toc_bin = self._data[self._archive_start + to:
                             self._archive_start + to + tl]
        pos = 0
        while pos < len(toc_bin):
            el, eo, dl, ul, cf, tc = struct.unpack(
                _ENTRY_FMT, toc_bin[pos:pos + _ENTRY_HDR_LEN])
            ns = pos + _ENTRY_HDR_LEN
            ne = toc_bin.find(b'\x00', ns)
            name = toc_bin[ns:ne].decode('utf-8')
            self.toc[name] = (eo, dl, ul, cf, tc.decode('ascii'))
            pos += el

    def extract(self, name):
        eo, dl, ul, cf, tc = self.toc[name]
        raw = self._data[self._archive_start + eo:
                         self._archive_start + eo + dl]
        if cf:
            raw = zlib.decompress(raw)
        return raw


# ---- 补丁核心 ----
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data")
PYZ_FILE = os.path.join(DATA_DIR, "PYZ.pyz")
MAIN_PYC = os.path.join(DATA_DIR, "main.pyc")

def patch_exe(src_path):
    base, ext = os.path.splitext(src_path)
    dst_path = f"{base}_Patched{ext}"

    if not os.path.exists(PYZ_FILE):
        raise FileNotFoundError(f"补丁数据缺失: {PYZ_FILE}")
    if not os.path.exists(MAIN_PYC):
        raise FileNotFoundError(f"补丁数据缺失: {MAIN_PYC}")

    print(f"[1/4] 复制: {os.path.basename(src_path)}")
    shutil.copy2(src_path, dst_path)

    print(f"[2/4] 读取文件结构...")
    a = MiniCArchive(dst_path)
    with open(dst_path, 'rb') as f:
        exe = bytearray(f.read())

    pyz_off, pyz_len, pyz_ulen, pyz_comp, pyz_type = a.toc['PYZ.pyz']
    main_off, main_len, main_ulen, main_comp, main_type = a.toc['main']
    arch_start = a._archive_start

    print(f"[3/4] 注入补丁...")
    # PYZ
    with open(PYZ_FILE, 'rb') as f:
        new_pyz = f.read()
    abs_pyz = arch_start + pyz_off
    if len(new_pyz) <= pyz_len:
        p = bytearray(new_pyz)
        p.extend(b'\x00' * (pyz_len - len(new_pyz)))
        exe[abs_pyz:abs_pyz + pyz_len] = p
    else:
        raise ValueError(f"PYZ太大 ({len(new_pyz)} > {pyz_len})")

    # main.py
    with open(MAIN_PYC, 'rb') as f:
        f.read(16)
        new_main = f.read()
    new_main_c = zlib.compress(new_main)
    abs_m = arch_start + main_off
    if len(new_main_c) <= main_len:
        p = bytearray(new_main_c)
        p.extend(b'\x00' * (main_len - len(new_main_c)))
        exe[abs_m:abs_m + main_len] = p

    # TOC
    cs = exe.rfind(_MEI_MAGIC)
    cookie_data = exe[cs:cs + _COOKIE_LEN]
    m, al, to, tl, pv, pln = struct.unpack(_COOKIE_FMT, cookie_data)
    toc_abs = arch_start + to
    toc_bin = bytes(exe[toc_abs:toc_abs + tl])

    new_toc = bytearray()
    pos = 0
    while pos < len(toc_bin):
        el, eo, dl, ul, cf, tc = struct.unpack(_ENTRY_FMT, toc_bin[pos:pos+_ENTRY_HDR_LEN])
        ns = pos + _ENTRY_HDR_LEN
        ne = toc_bin.find(b'\x00', ns)
        name = toc_bin[ns:ne].decode('utf-8')
        if name == 'PYZ.pyz':
            new_toc.extend(struct.pack(_ENTRY_FMT, el, eo, pyz_len, pyz_ulen, cf, tc))
            new_toc.extend(toc_bin[ns:pos+el])
        elif name == 'main':
            new_toc.extend(struct.pack(_ENTRY_FMT, el, eo, main_len, len(new_main), 1, tc))
            new_toc.extend(toc_bin[ns:pos+el])
        else:
            new_toc.extend(toc_bin[pos:pos+el])
        pos += el
    exe[toc_abs:toc_abs+tl] = bytes(new_toc[:tl])

    with open(dst_path, 'wb') as f:
        f.write(bytes(exe))

    # Verify
    v = MiniCArchive(dst_path)
    v.extract('PYZ.pyz')
    v.extract('main')

    print(f"[4/4] 破解完成！")
    print(f"    输出: {os.path.basename(dst_path)}")
    print(f"    大小: {os.path.getsize(dst_path):,} 字节")
    return dst_path


# ---- GUI ----
class PatcherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YOLO Annotation Tool Pro Patcher v1.0")
        self.root.geometry("500x260")
        self.root.resizable(False, False)
        self._check_data()

        tk.Label(self.root, text="YOLO Annotation Tool Pro 一键破解补丁",
                 font=("Microsoft YaHei", 14, "bold")).pack(pady=(20, 5))
        tk.Label(self.root, text="选择要破解的 exe 文件，自动生成 _Patched 版本",
                 font=("Microsoft YaHei", 9), fg="#555").pack(pady=(0, 15))

        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        self.path_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.path_var,
                 width=45, font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(frame, text="浏览...", command=self._browse,
                  font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="就绪")
        self.patch_btn = tk.Button(self.root, text="开始破解",
                                   command=self._patch,
                                   font=("Microsoft YaHei", 11, "bold"),
                                   bg="#4CAF50", fg="white",
                                   width=15, height=1, state=tk.DISABLED)
        self.patch_btn.pack(pady=(10, 5))

        self.progress_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.progress_var,
                 font=("Microsoft YaHei", 9), fg="#333").pack()
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Microsoft YaHei", 9), fg="#888").pack(pady=(5, 0))
        tk.Label(self.root, text="破解后所有VIP功能可用，无需联网",
                 font=("Microsoft YaHei", 8), fg="#aaa").pack()

    def _check_data(self):
        for f in ["PYZ.pyz", "main.pyc"]:
            if not os.path.exists(os.path.join(DATA_DIR, f)):
                messagebox.showerror("初始化失败", f"缺少补丁数据: {f}")
                self.root.after(100, self.root.destroy)
                return

    def _browse(self):
        path = filedialog.askopenfilename(
            title="选择 YOLO_Annotation_Tool_Pro.exe",
            filetypes=[("EXE 文件", "*.exe"), ("所有文件", "*.*")])
        if path:
            self.path_var.set(path)
            self.patch_btn.config(state=tk.NORMAL)

    def _patch(self):
        src = self.path_var.get()
        if not src or not os.path.exists(src):
            messagebox.showerror("错误", "请选择有效的 EXE 文件")
            return

        self.patch_btn.config(state=tk.DISABLED, text="破解中...")
        self.progress_var.set("正在破解，请稍候...")
        self.root.update()

        try:
            dst = patch_exe(src)
            self.status_var.set("破解成功！")
            self.progress_var.set(f"输出: {os.path.basename(dst)}")
            messagebox.showinfo(
                "破解成功",
                f"已生成破解版文件:\n{dst}\n\n"
                f"所有 VIP 功能已解锁！\n"
                f"运行前请关闭原版程序")
            self.root.destroy()
        except Exception as e:
            self.progress_var.set("破解失败")
            messagebox.showerror("破解失败", str(e))
            self.patch_btn.config(text="开始破解", state=tk.NORMAL)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        try:
            dst = patch_exe(sys.argv[1])
        except Exception as e:
            print(f"[!] 失败: {e}")
            sys.exit(1)
    else:
        PatcherApp().run()
