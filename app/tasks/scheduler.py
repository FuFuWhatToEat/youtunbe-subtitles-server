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
        self.completed_tasks = {}  # 缓存已完成任务

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
        # 生成task_id
        import uuid

        task_id = str(uuid.uuid4())
        # 创建job
        job = self.scheduler.add_job(
            self.download_service.extract_subtitles, args=[url, task_id]
        )
        logger.debug(f"Created job with ID: {task_id}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        logger.debug(f"Getting status for task: {task_id}")

        # 1. 检查缓存中是否有已完成任务
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]

        # 2. 检查字幕文件是否存在(支持.en.vtt后缀)
        from pathlib import Path
        from app.config import Config

        subtitles_dir = Path(Config.SUBTITLES_DIR)
        # 精确匹配以task_id开头且以.vtt结尾的文件
        matching_files = list(subtitles_dir.glob(f"{task_id}*.vtt"))
        if matching_files:
            sub_file = matching_files[0]  # 取第一个匹配的文件
            with open(sub_file, "r", encoding="utf-8") as f:
                content = f.read()
            result = {"status": "completed", "path": str(sub_file), "content": content}
            self.completed_tasks[task_id] = result
            return result

        # 3. 检查任务是否还在运行
        job = self.scheduler.get_job(task_id)
        if job:
            if not job.ready():
                logger.debug(f"Task {task_id} still processing")
                return {"status": "processing"}

            # 处理已完成但未生成文件的任务
            result = job.result or {}
            if result.get("status") == "success":
                logger.info(f"Task {task_id} completed successfully")
                result = {
                    "status": "completed",
                    "content": result.get("content"),
                    "path": result.get("path"),
                }
                self.completed_tasks[task_id] = result
                return result
            else:
                logger.warning(
                    f"Task {task_id} failed: {result.get('message', 'Unknown error')}"
                )
                return {"status": "error", "message": result.get("message")}

        # 4. 任务不存在或已完成但无结果
        logger.warning(f"Task not found: {task_id}")
        return {"status": "not_found"}
