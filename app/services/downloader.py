import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, cast
from yt_dlp import YoutubeDL
from app.config import Config

logger = logging.getLogger(__name__)


class DownloadService:
    def __init__(self):
        self.subtitles_dir = Config.SUBTITLES_DIR
        logger.info(
            f"Initialized DownloadService with output dir: {self.subtitles_dir}"
        )

    def extract_subtitles(self, url: str) -> Dict[str, Any]:
        """使用yt-dlp API提取字幕"""
        logger.info(f"Starting subtitle extraction for URL: {url}")
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["zh", "en"],
            "skip_download": True,
            "quiet": True,
            "outtmpl": str(self.subtitles_dir / "%(id)s.%(ext)s"),
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                logger.debug(f"YT-DLP options: {ydl_opts}")
                info = ydl.extract_info(url, download=True)
                sanitized = cast(Dict[str, Any], ydl.sanitize_info(info))
                logger.debug(f"Video info: {json.dumps(sanitized, indent=2)}")

                # 安全获取字幕文件路径
                requested_subs = sanitized.get("requested_subtitles", {})
                if not isinstance(requested_subs, dict) or not requested_subs:
                    logger.warning("No subtitles generated for video")
                    return {"status": "error", "message": "No subtitles generated"}

                # 获取第一个字幕文件信息
                sub_info = next(iter(requested_subs.values()), {})
                if not isinstance(sub_info, dict):
                    logger.error("Invalid subtitle info format")
                    return {"status": "error", "message": "Invalid subtitle info"}

                filepath = sub_info.get("filepath", "")
                if not filepath or not isinstance(filepath, str):
                    logger.error("Subtitle file path not found in response")
                    return {"status": "error", "message": "Subtitle path not found"}

                sub_path = Path(filepath)
                if sub_path.exists():
                    with open(sub_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    logger.info(f"Successfully extracted subtitles to: {sub_path}")
                    return {
                        "status": "success",
                        "content": content,
                        "path": str(sub_path),
                    }
                logger.error(f"Subtitle file not found at: {sub_path}")
                return {"status": "error", "message": "Subtitle file not found"}

        except Exception as e:
            logger.error(f"Subtitle extraction failed: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
