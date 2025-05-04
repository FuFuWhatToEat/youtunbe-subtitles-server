import logging
from flask import request
from typing import Dict, Any, Optional, Union

from flask_restx import Resource
from app.tasks.scheduler import TaskScheduler

logger = logging.getLogger(__name__)

# 创建一个全局单例调度器实例
task_scheduler = TaskScheduler()


class SubtitleExtraction(Resource):
    def __init__(self):
        self.scheduler = task_scheduler

    def post(self) -> Union[Dict[str, Any], tuple]:
        """创建新的字幕提取任务"""
        data = request.get_json()
        if not data or "url" not in data:
            return {"error": "URL is required in JSON payload"}, 400

        task_id = self.scheduler.add_subtitle_task(url=data["url"])
        return {
            "task_id": task_id,
            "message": "Subtitle extraction started",
            "url": data["url"],
        }

    def get(self, task_id: Optional[str] = None) -> Union[Dict[str, Any], tuple]:
        """获取字幕提取结果"""
        if task_id is None:
            return {"error": "Task ID is required"}, 400

        status = self.scheduler.get_task_status(task_id)
        if status.get("status") == "completed":
            return {
                "status": "completed",
                "content": status.get("content", ""),
                "path": status.get("path", ""),
            }
        return {
            "status": status.get("status", "error"),
            "message": status.get("message", "Unknown error"),
        }
