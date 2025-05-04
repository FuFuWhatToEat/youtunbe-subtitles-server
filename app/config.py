import os
from pathlib import Path


class Config:
    # 基础目录
    BASE_DIR = Path(__file__).parent.parent

    # 任务配置
    MAX_CONCURRENT_TASKS = 3  # 最大并行任务数
    TASK_TIMEOUT = 3600  # 任务超时时间(秒)

    # 存储配置
    DOWNLOAD_DIR = BASE_DIR / "downloads"
    SUBTITLES_DIR = BASE_DIR / "subtitles"
    TEMP_DIR = BASE_DIR / "temp"
    LOG_DIR = BASE_DIR / "logs"

    # 确保目录存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(SUBTITLES_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    @classmethod
    def init_app(cls, app):
        """初始化Flask应用配置"""
        app.config.update(
            {
                "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16MB上传限制
                "SECRET_KEY": os.getenv("FLASK_SECRET_KEY", "dev-key"),
            }
        )
