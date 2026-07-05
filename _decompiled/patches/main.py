import sys

def _bootstrap_http_subcommand():
    """打包 HTTP 子进程：须在 PySide6 / SAM3 导入之前退出。"""
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
        auth_result = loading.auth_result
        if auth_result and not auth_result.ok:
            from app_widgets.zh_message_box import critical_ok
            detail = auth_result.error_message or ""
            if auth_result.update_message:
                detail += "\n\n" + auth_result.update_message
            critical_ok("启动失败", f"\n{detail}")
            sys.exit(1)

        # 设置版本
        from app_config.version import VERSION
        from app_services.app_version_store import set_startup_versions
        set_startup_versions("9.9.9", "9.9.9")

        # 启动主窗口
        from app_main.main_window import MainWindow
        window = MainWindow()
        global_exception_handler.set_main_window(window)
        try:
            window.apply_vip_gates()
        except Exception as e:
            print(f"apply_vip_gates error: {e}")
        window.show()

        # 第一次启动时提示打开最近项目
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, window.annotation_page.prompt_open_recent_project)

        # 进入 Qt 事件循环（必须有，否则窗口一闪就退）
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    if sys.platform == "nt":
        multiprocessing.set_start_method("forkserver", force=True)
    main()

