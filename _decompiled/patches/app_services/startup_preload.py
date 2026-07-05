"""
启动阶段主线程预导入重模块，缩短进入主界面后的首屏等待。
"""
def preload_startup_modules():
    import app_main.main_window
    import app_pages.annotation_page
    import app_pages.training_page
    import app_pages.validation_page
    import app_pages.http_service_page
