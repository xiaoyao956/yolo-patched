# YOLO Annotation Tool Pro - Patched

YOLO Annotation Tool Pro 破解版 — 从源码构建可运行的补丁程序。

## 功能特点

- ✅ 去除所有联网校验 — 完全离线运行
- ✅ 去除 VIP 校验 — 全部功能解锁，无试用期
- ✅ 去除 EULA 弹窗 — 启动自动跳过
- ✅ 去除版本强制更新 — 不会提示"有新版本"
- ✅ 版本号改为 v9.9.9
- ✅ 保留全部核心功能（训练/标注/验证/HTTP服务/模型导出等）

## 仓库结构

```
├── _decompiled/
│   ├── patches/                  ← 补丁后的 Python 源码（13 个文件）
│   │   ├── main.py               ← 入口脚本（无网络校验）
│   │   ├── app_config/
│   │   │   └── version.py        ← 版本号 9.9.9
│   │   ├── app_main/
│   │   │   └── eula_dialog.py    ← 跳过 EULA 弹窗
│   │   ├── app_network/
│   │   │   ├── fn_net_work.py    ← 所有 API 返回模拟成功
│   │   │   └── fn_app_config.py  ← 服务器地址占位
│   │   └── app_services/
│   │       ├── vip_license_service.py  ← can_use/require_feature 永恒 True
│   │       ├── vip_feature_map.py      ← 全部功能永久开启
│   │       ├── startup_auth_worker.py  ← 跳过联网认证
│   │       ├── fn_session.py           ← 模拟会话
│   │       ├── app_version_store.py    ← 版本锁定 9.9.9
│   │       └── device_identity_store.py ← 指纹占位
│   ├── pyc311/                  ← Python 3.11 编译后的 bytecode
│   ├── build/
│   │   └── PYZ.pyz              ← 补丁后的模块归档（80 MB）
│   ├── patch_inplace.py         ← 原地打补丁核心脚本
│   ├── rebuild_full.py          ← 完整 CArchive 重建脚本
│   └── generate_patches.py      ← 补丁代码生成器
├── _patcher/
│   └── patch_gui.py             ← GUI 补丁工具
└── README.md
```

## 从源码构建 YOLO_Annotation_Tool_Pro_Patched.exe

### 前置要求
- Python 3.11 — 编译 bytecode 版本匹配
- PyInstaller 6.x — `pip install pyinstaller`
- 原版 `YOLO_Annotation_Tool_Pro.exe` — 放入仓库根目录

### 构建步骤

```bash
# 1. 编译补丁源码为 Python 3.11 bytecode
python -c "
import py_compile, os

for root, dirs, files in os.walk('_decompiled/patches'):
    for f in files:
        if f.endswith('.py'):
            src = os.path.join(root, f)
            rel = os.path.relpath(src, '_decompiled/patches')
            dst = os.path.join('_decompiled/pyc311', rel[:-3] + '.pyc')
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            py_compile.compile(src, cfile=dst, doraise=True)
            print(f'  OK: {rel}')
"

# 2. 构建补丁后的 PYZ
python _decompiled/generate_patches.py

# 3. 对原始 EXE 打补丁
python _decompiled/patch_inplace.py

# 输出 YOLO_Annotation_Tool_Pro_Patched.exe
```

### 快速构建（一步完成）

```bash
python _decompiled/rebuild_full.py
```

### 使用 GUI 补丁工具
```bash
python _patcher/patch_gui.py
```

## 补丁原理

详见补丁工具仓库：[xiaoyao956/yolo-patcher](https://github.com/xiaoyao956/yolo-patcher)

核心原理：**二进制原地替换**。在 PYZ 和 main.py 原偏移处，用补丁后的代码覆盖（不足部分 \x00 填充），再更新 TOC 表。

### 涉及修改的模块

| 模块 | 修改内容 |
|------|----------|
| main.py | 移除 EULA + 网络认证 + 版本校验 + 心跳 |
| app_config/version | 版本号 9.9.9 |
| app_services/vip_license_service | can_use/require_feature 返回 True |
| app_services/vip_feature_map | 全部功能永久开启 |
| app_services/startup_auth_worker | 跳过启动认证 |
| app_network/fn_net_work | 所有 API 模拟成功 |
| app_network/fn_app_config | 服务器地址本地占位 |
| app_main/eula_dialog | 跳过 EULA 弹窗 |
| app_services/fn_session | 模拟会话单例 |
| app_services/app_version_store | 版本锁定 9.9.9 |
| app_services/device_identity_store | 设备指纹占位 |
| app_services/startup_preload | 保持原逻辑 |

## 运行

构建完成后：

1. 确保 `_internal/` 目录与 exe 在同一目录下（从原版安装复制）
2. 双击 `YOLO_Annotation_Tool_Pro_Patched.exe` 即可运行

## 相关仓库

- [xiaoyao956/yolo-patcher](https://github.com/xiaoyao956/yolo-patcher) — 独立补丁工具（可直接对任意版本 exe 打补丁，无需 Python 环境）
