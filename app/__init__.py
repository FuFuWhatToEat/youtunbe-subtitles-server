import logging
from logging.config import dictConfig
from flask import Flask, request
from flask_restx import Api
from flask_cors import CORS
from app.config import Config


def configure_logging():
    """配置应用程序日志"""
    log_config = {
        "version": 1,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": Config.LOG_DIR / "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "standard",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": "DEBUG",
            },
            "app": {"level": "DEBUG", "propagate": True},
            "werkzeug": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    dictConfig(log_config)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def create_app():
    """创建并配置Flask应用"""
    # 配置日志
    configure_logging()

    app = Flask(__name__)

    # 配置CORS
    CORS(app)

    # 配置应用
    Config.init_app(app)

    # 添加请求日志中间件
    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status}")
        return response

    # 创建API并配置Swagger文档
    api = Api(
        app,
        version="1.0",
        title="YouTube字幕提取API",
        description="用于提取YouTube视频字幕的REST API",
        doc="/docs",  # Swagger UI路径
    )

    # 从api.resources模块导入资源并注册
    from app.api.resources import SubtitleExtraction

    api.add_resource(SubtitleExtraction, "/subtitles", "/subtitles/<string:task_id>")

    return app
