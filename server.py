# -*- coding: utf-8 -*-
"""
DH DOW Server - FastAPI Web Application & Backend APIs
Supports PyInstaller standalone bundle resource path resolution.
"""

import os
import sys
import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Ensure PyInstaller temp directory is in sys.path
if hasattr(sys, '_MEIPASS'):
    meipass_path = str(Path(sys._MEIPASS).resolve())
    if meipass_path not in sys.path:
        sys.path.insert(0, meipass_path)

def get_resource_path(relative_path: str) -> Path:
    """Resolve resource path for both development and PyInstaller executable."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

from engine import engine, DEFAULT_DOWNLOAD_DIR

app = FastAPI(title="DH DOW Server", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve static directory
STATIC_DIR = get_resource_path("static")
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class AnalyzeRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    save_dir: Optional[str] = None
    quality: Optional[str] = "best"


class SelectFolderRequest(BaseModel):
    current_dir: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>DH DOW - Modern Video Downloader</h1><p>Static files missing</p>"


@app.post("/api/analyze")
async def analyze_video(req: AnalyzeRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="URL không hợp lệ (Invalid URL)")
    info = engine.analyze_url(req.url.strip())
    return JSONResponse(content=info)


@app.post("/api/download")
async def start_download(req: DownloadRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="URL không hợp lệ (Invalid URL)")
    task_id = engine.start_download(
        url=req.url.strip(),
        save_dir=req.save_dir or engine.download_dir,
        quality=req.quality or "best"
    )
    return JSONResponse(content={"status": "success", "task_id": task_id})


@app.get("/api/progress/{task_id}")
async def get_progress(task_id: str):
    task = engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task)


@app.get("/api/history")
async def get_history():
    return JSONResponse(content={"history": engine.get_history()})


@app.post("/api/history/clear")
async def clear_history():
    engine.clear_history()
    return JSONResponse(content={"status": "success"})


@app.post("/api/select-folder")
async def select_folder():
    """Trigger Windows folder selection dialog using tkinter."""
    selected = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(initialdir=engine.download_dir, title="Chọn thư mục lưu DH DOW")
        root.destroy()
        if folder:
            selected = str(Path(folder).resolve())
            engine.download_dir = selected
    except Exception as e:
        print(f"File dialog error: {e}")
        
    return JSONResponse(content={
        "status": "success" if selected else "cancelled",
        "save_dir": engine.download_dir
    })


@app.post("/api/open-folder")
async def open_folder():
    target = engine.download_dir
    if os.path.exists(target):
        if sys.platform == "win32":
            os.startfile(target)
        else:
            subprocess.Popen(["xdg-open", target])
        return JSONResponse(content={"status": "success"})
    return JSONResponse(content={"status": "error", "message": "Folder does not exist"})


@app.get("/api/info")
async def get_info():
    return JSONResponse(content={
        "app_name": "DH DOW",
        "version": "2.0.0",
        "download_dir": engine.download_dir,
        "contact": {
            "phone": "0862.610.313",
            "facebook": "https://www.facebook.com/ducduy2512",
            "zalo": "0862.610.313"
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=5820, reload=True)
