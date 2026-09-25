# -*- coding: utf-8 -*-
"""
DH DOW Engine - Core Downloader Module
Integrates `you_get` with fallback to `yt-dlp` for maximum reliability.
"""

import os
import sys
import json
import threading
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Attempt to import you_get natively
try:
    import you_get
    from you_get.common import url_to_module, parse_host
    HAS_YOU_GET = True
except ImportError:
    HAS_YOU_GET = False

# Attempt to import yt_dlp for fallback/enhanced formats
try:
    import yt_dlp
    HAS_YT_DLP = True
except ImportError:
    HAS_YT_DLP = False

DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads" / "DH_DOW")
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)


class DownloaderTask:
    def __init__(self, task_id: str, url: str, save_dir: str, quality: str = "best", engine: str = "auto"):
        self.task_id = task_id
        self.url = url
        self.save_dir = save_dir or DEFAULT_DOWNLOAD_DIR
        self.quality = quality
        self.engine = engine
        
        # Status tracking
        self.status = "queued"  # queued, analyzing, downloading, completed, error
        self.progress = 0.0
        self.title = "Đang tải thông tin..."
        self.platform = "Unknown"
        self.thumbnail = ""
        self.filename = ""
        self.speed = "0 KB/s"
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.eta = "--:--"
        self.error_msg = ""
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "url": self.url,
            "save_dir": self.save_dir,
            "quality": self.quality,
            "engine": self.engine,
            "status": self.status,
            "progress": round(self.progress, 1),
            "title": self.title,
            "platform": self.platform,
            "thumbnail": self.thumbnail,
            "filename": self.filename,
            "speed": self.speed,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "eta": self.eta,
            "error_msg": self.error_msg,
            "created_at": self.created_at
        }


class DHDowEngine:
    def __init__(self):
        self.tasks: Dict[str, DownloaderTask] = {}
        self.history_file = Path("download_history.json")
        self.download_dir = DEFAULT_DOWNLOAD_DIR
        self.history: List[Dict[str, Any]] = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def detect_platform(self, url: str) -> str:
        url_lower = url.lower()
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube"
        elif "tiktok.com" in url_lower:
            return "TikTok"
        elif "facebook.com" in url_lower or "fb.watch" in url_lower:
            return "Facebook"
        elif "bilibili.com" in url_lower or "b23.tv" in url_lower:
            return "Bilibili"
        elif "instagram.com" in url_lower:
            return "Instagram"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "Twitter/X"
        elif "soundcloud.com" in url_lower:
            return "SoundCloud"
        elif "vimeo.com" in url_lower:
            return "Vimeo"
        else:
            return "Web Video"

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Extract metadata (Title, Thumbnail, Platform, Formats) using yt_dlp or you_get."""
        platform = self.detect_platform(url)
        info = {
            "url": url,
            "platform": platform,
            "title": "Untitled Video",
            "thumbnail": "",
            "duration": "N/A",
            "formats": [
                {"id": "best", "label": "Chất lượng tốt nhất (Best Quality)"},
                {"id": "1080p", "label": "Full HD (1080p)"},
                {"id": "720p", "label": "HD (720p)"},
                {"id": "480p", "label": "Standard (480p)"},
                {"id": "mp3", "label": "Chỉ âm thanh (Audio MP3)"}
            ]
        }

        # Try yt_dlp for rich metadata first
        if HAS_YT_DLP:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'skip_download': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    extracted = ydl.extract_info(url, download=False)
                    if extracted:
                        info["title"] = extracted.get("title") or info["title"]
                        info["thumbnail"] = extracted.get("thumbnail") or info["thumbnail"]
                        dur = extracted.get("duration")
                        if dur:
                            m, s = divmod(dur, 60)
                            h, m = divmod(m, 60)
                            info["duration"] = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"
                        return info
            except Exception as e:
                print(f"yt_dlp metadata analysis notice: {e}")

        # Fallback to simple title detection if needed
        info["title"] = f"{platform} Video - {url.split('/')[-1][:20]}"
        return info

    def start_download(self, url: str, save_dir: Optional[str] = None, quality: str = "best") -> str:
        task_id = f"task_{int(time.time() * 1000)}"
        target_dir = save_dir or self.download_dir
        os.makedirs(target_dir, exist_ok=True)

        task = DownloaderTask(task_id, url, target_dir, quality)
        task.platform = self.detect_platform(url)
        self.tasks[task_id] = task

        # Start download thread
        thread = threading.Thread(target=self._download_worker, args=(task_id,), daemon=True)
        thread.start()
        return task_id

    def _download_worker(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = "analyzing"
        task.title = f"Đang phân tích {task.platform}..."

        # 1. Try downloading using you_get engine via python call / CLI
        success = False
        
        # First attempt with yt-dlp if installed (provides smooth real-time progress)
        if HAS_YT_DLP:
            try:
                task.status = "downloading"
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                        downloaded = d.get('downloaded_bytes') or 0
                        if total > 0:
                            task.progress = (downloaded / total) * 100
                        task.downloaded_bytes = downloaded
                        task.total_bytes = total
                        
                        # Speed & ETA
                        speed_val = d.get('speed') or 0
                        if speed_val > 1024 * 1024:
                            task.speed = f"{speed_val / (1024 * 1024):.1f} MB/s"
                        elif speed_val > 1024:
                            task.speed = f"{speed_val / 1024:.1f} KB/s"
                        else:
                            task.speed = f"{speed_val:.0f} B/s"
                            
                        eta_val = d.get('eta')
                        if eta_val:
                            m, s = divmod(eta_val, 60)
                            task.eta = f"{int(m):02d}:{int(s):02d}"

                    elif d['status'] == 'finished':
                        task.progress = 100.0
                        task.status = "completed"
                        task.filename = os.path.basename(d.get('filename', 'video.mp4'))

                ydl_opts = {
                    'outtmpl': os.path.join(task.save_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True
                }

                if task.quality == 'mp3':
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                elif task.quality == '1080p':
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                elif task.quality == '720p':
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                elif task.quality == '480p':
                    ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(task.url, download=True)
                    if info_dict:
                        task.title = info_dict.get('title', task.title)
                        task.thumbnail = info_dict.get('thumbnail', '')
                
                success = True
                task.status = "completed"
                task.progress = 100.0
            except Exception as e:
                print(f"yt-dlp error, falling back to you-get: {e}")
                success = False

        # If yt-dlp is not used or failed, fallback to you_get
        if not success and HAS_YOU_GET:
            try:
                task.status = "downloading"
                cmd = [sys.executable, "-m", "you_get", "-o", task.save_dir, task.url]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore'
                )

                for line in process.stdout:
                    line_str = line.strip()
                    if "title:" in line_str.lower():
                        task.title = line_str.split(":", 1)[-1].strip()
                    elif "%" in line_str:
                        # Extract percentage like 45.2%
                        parts = line_str.split()
                        for p in parts:
                            if p.endswith("%"):
                                try:
                                    task.progress = float(p.rstrip("%"))
                                except ValueError:
                                    pass

                process.wait()
                if process.returncode == 0:
                    task.status = "completed"
                    task.progress = 100.0
                    success = True
                else:
                    task.error_msg = f"you-get exited with code {process.returncode}"
            except Exception as e:
                task.error_msg = str(e)

        if task.status == "completed":
            # Record in history
            hist_item = task.to_dict()
            self.history.insert(0, hist_item)
            self._save_history()
        elif task.status != "completed":
            task.status = "error"
            if not task.error_msg:
                task.error_msg = "Không thể tải video này. Vui lòng kiểm tra lại đường dẫn."

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def clear_history(self):
        self.history = []
        self._save_history()


# Global engine instance
engine = DHDowEngine()
