import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, cast
from yt_dlp import YoutubeDL
from app.config import Config

logger = logging.getLogger(__name__)


class DownloadService:
    def __init__(self):
        self.subtitles_dir = Config.SUBTITLES_DIR
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        logger.info(
            f"Initialized DownloadService with output dir: {self.subtitles_dir}"
        )

    def extract_subtitles(self, url: str, task_id: str) -> Dict[str, Any]:
        """使用yt-dlp API提取字幕"""
        logger.info(f"Starting subtitle extraction for URL: {url}, task_id: {task_id}")

        for attempt in range(self.max_retries):
            try:
                ydl_opts = {
                    "writesubtitles": True,
                    "writeautomaticsub": True,
                    "subtitleslangs": ["zh", "en"],
                    "skip_download": True,
                    "quiet": True,
                    "outtmpl": str(self.subtitles_dir / f"{task_id}"),
                    "socket_timeout": 30,
                    "retries": 3,
                    "extractor_retries": 3,
                    "fragment_retries": 3,
                    "file_access_retries": 3,
                    "http_chunk_size": 10485760,
                    "buffersize": 1024,
                    "nocheckcertificate": True,
                    "ignoreerrors": True,
                    "no_warnings": False,
                    "verbose": True,
                    # 新增配置
                    "postprocessors": [
                        {
                            "key": "FFmpegSubtitlesConvertor",
                            "format": "vtt",
                        }
                    ],
                    "keepvideo": False,
                    "writedescription": False,
                    "writeinfojson": False,
                    "writethumbnail": False,
                    "writesubtitles": True,
                    "writeautomaticsub": True,
                    "subtitlesformat": "vtt",
                    "subtitleslangs": ["zh", "en"],
                    "skip_download": True,
                    "format": "best",
                }

                with YoutubeDL(ydl_opts) as ydl:
                    logger.debug(f"YT-DLP options: {ydl_opts}")
                    info = ydl.extract_info(url, download=True)
                    sanitized = cast(Dict[str, Any], ydl.sanitize_info(info))

                    # 记录视频信息
                    logger.debug(f"Video title: {sanitized.get('title')}")
                    logger.debug(
                        f"Available subtitles: {sanitized.get('subtitles', {})}"
                    )
                    logger.debug(
                        f"Automatic captions: {sanitized.get('automatic_captions', {})}"
                    )

                    # 获取字幕文件路径
                    requested_subs = sanitized.get("requested_subtitles", {})
                    if not isinstance(requested_subs, dict) or not requested_subs:
                        logger.warning("No subtitles found in video info")
                        if attempt < self.max_retries - 1:
                            logger.info(
                                f"Retrying in {self.retry_delay} seconds... (Attempt {attempt + 1}/{self.max_retries})"
                            )
                            time.sleep(self.retry_delay)
                            continue
                        return {"status": "error", "message": "No subtitles found"}

                    # 尝试获取字幕文件
                    for lang, sub_info in requested_subs.items():
                        if not isinstance(sub_info, dict):
                            continue

                        filepath = sub_info.get("filepath", "")
                        if not filepath or not isinstance(filepath, str):
                            logger.warning(f"No filepath found for {lang} subtitles")
                            continue

                        sub_path = Path(filepath)
                        if sub_path.exists():
                            try:
                                with open(sub_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                if content and len(content.strip()) > 0:
                                    logger.info(
                                        f"Successfully extracted subtitles to: {sub_path}"
                                    )
                                    return {
                                        "status": "success",
                                        "content": content,
                                        "path": str(sub_path),
                                    }
                                else:
                                    logger.warning(f"Empty subtitle file for {lang}")
                            except Exception as e:
                                logger.error(f"Error reading subtitle file: {str(e)}")
                                continue

                    logger.error("Failed to extract any subtitle")
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                    return {"status": "error", "message": "Failed to extract subtitles"}

            except Exception as e:
                logger.error(
                    f"Subtitle extraction failed (Attempt {attempt + 1}/{self.max_retries}): {str(e)}",
                    exc_info=True,
                )
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Max retries exceeded"}
