import json
import logging
import time
import requests
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

    def _download_subtitle_directly(
        self, url: str, task_id: str, lang: str
    ) -> Optional[Path]:
        """直接下载字幕文件"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            logger.debug(f"Attempting to download subtitle from URL: {url}")
            response = requests.get(url, headers=headers, timeout=30)

            # 记录响应状态和头信息
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")

            response.raise_for_status()

            # 检查响应内容
            content = response.text
            if not content or len(content.strip()) == 0:
                logger.error("Received empty subtitle content")
                return None

            logger.debug(f"Received subtitle content length: {len(content)}")

            sub_path = self.subtitles_dir / f"{task_id}.{lang}.vtt"
            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(content)
            return sub_path
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while downloading subtitle: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while downloading subtitle: {str(e)}")
            return None

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
                }

                with YoutubeDL(ydl_opts) as ydl:
                    logger.debug(f"YT-DLP options: {ydl_opts}")
                    info = ydl.extract_info(url, download=False)
                    sanitized = cast(Dict[str, Any], ydl.sanitize_info(info))

                    # 记录视频信息
                    logger.debug(f"Video title: {sanitized.get('title')}")
                    logger.debug(
                        f"Available subtitles: {sanitized.get('subtitles', {})}"
                    )
                    logger.debug(
                        f"Automatic captions: {sanitized.get('automatic_captions', {})}"
                    )

                    # 获取字幕URL
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

                    # 尝试直接下载字幕
                    for lang, sub_info in requested_subs.items():
                        if not isinstance(sub_info, dict):
                            continue

                        sub_url = sub_info.get("url")
                        if not sub_url:
                            logger.warning(f"No URL found for {lang} subtitles")
                            continue

                        logger.info(f"Attempting to download {lang} subtitles")
                        sub_path = self._download_subtitle_directly(
                            sub_url, task_id, lang
                        )
                        if sub_path and sub_path.exists():
                            with open(sub_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            logger.info(
                                f"Successfully downloaded subtitles to: {sub_path}"
                            )
                            return {
                                "status": "success",
                                "content": content,
                                "path": str(sub_path),
                            }

                    logger.error("Failed to download any subtitle")
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                    return {
                        "status": "error",
                        "message": "Failed to download subtitles",
                    }

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
