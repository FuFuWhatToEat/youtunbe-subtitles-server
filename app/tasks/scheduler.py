import logging
from typing import Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from app.services.downloader import DownloadService
from app.config import Config

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        self.download_service = DownloadService()
        self.jobstores = {"default": MemoryJobStore()}
        self.executors = {"default": ThreadPoolExecutor(Config.MAX_CONCURRENT_TASKS)}

        logger.info("Initializing TaskScheduler")
        logger.debug(f"Max concurrent tasks: {Config.MAX_CONCURRENT_TASKS}")

        self.scheduler = BackgroundScheduler(
            jobstores=self.jobstores, executors=self.executors
        )
        self.scheduler.start()
        logger.info("TaskScheduler started")

    def add_subtitle_task(self, url: str) -> str:
        """添加字幕提取任务"""
        logger.info(f"Adding new subtitle task for URL: {url}")
        job = self.scheduler.add_job(
            self.download_service.extract_subtitles, args=[url]
        )
        logger.debug(f"Created job with ID: {job.id}")
        return job.id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        logger.debug(f"Getting status for task: {task_id}")
        job = self.scheduler.get_job(task_id)
        if not job:
            logger.warning(f"Task not found: {task_id}")
            return {"status": "not_found"}

        if not job.ready():
            logger.debug(f"Task {task_id} still processing")
            return {"status": "processing"}

        result = job.result
        if result and result.get("status") == "success":
            logger.info(f"Task {task_id} completed successfully")
        else:
            logger.warning(
                f"Task {task_id} failed: {result.get('message', 'Unknown error')}"
            )

        return {
            "status": "completed",
            "content": result.get("content"),
            "path": result.get("path"),
        }
