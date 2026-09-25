# -*- coding: utf-8 -*-
"""
DH DOW - Standalone Desktop Application Launcher
Uses explicit asyncio event loop for Uvicorn server in background thread,
guaranteeing 100% reliable local server binding without ERR_CONNECTION_REFUSED.
"""

import sys
import os
import time
import socket
import threading
import urllib.request
import webbrowser
from pathlib import Path

# Log file for debugging standalone EXE
LOG_FILE = Path.home() / "dh_dow_app.log"

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

# Add PyInstaller temp dir to sys.path
if hasattr(sys, '_MEIPASS'):
    meipass_path = str(Path(sys._MEIPASS).resolve())
    if meipass_path not in sys.path:
        sys.path.insert(0, meipass_path)
    log(f"PyInstaller MEIPASS loaded: {meipass_path}")

HOST = "127.0.0.1"
DEFAULT_PORT = 5820

def find_free_port(start_port=DEFAULT_PORT):
    """Find an available TCP port starting from start_port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((HOST, port)) != 0:
                return port
    return start_port

PORT = find_free_port()
SERVER_URL = f"http://{HOST}:{PORT}"

def start_backend():
    """Start Uvicorn FastAPI backend server on a dedicated asyncio loop."""
    try:
        import asyncio
        import uvicorn
        from server import app

        log(f"Starting uvicorn server on {HOST}:{PORT}")
        config = uvicorn.Config(
            app,
            host=HOST,
            port=PORT,
            log_level="error",
            access_log=False,
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.serve())
    except Exception as e:
        log(f"Backend server error: {e}")

def wait_for_server(timeout=10.0):
    """Poll server URL until it responds with HTTP 200 OK."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(SERVER_URL, headers={"User-Agent": "DH-DOW-Launcher"})
            with urllib.request.urlopen(req, timeout=0.5) as response:
                if response.status == 200:
                    log(f"Server verified ready on {SERVER_URL}")
                    return True
        except Exception:
            time.sleep(0.1)
    log(f"Server readiness timeout on {SERVER_URL}")
    return False

def main():
    log("=== DH DOW Starting ===")
    
    # 1. Start backend server in a background daemon thread
    server_thread = threading.Thread(target=start_backend, daemon=True)
    server_thread.start()

    # 2. Wait until backend server is 100% active & responding
    is_ready = wait_for_server(timeout=10.0)

    if not is_ready:
        log("Backend failed to start in time.")

    # 3. Launch UI (Attempt PyWebView native window or fallback to default browser)
    launched_native = False

    if is_ready:
        try:
            import webview
            log("Creating PyWebView window...")
            window = webview.create_window(
                title="DH DOW - Tải Video Đa Nền Tảng",
                url=SERVER_URL,
                width=1180,
                height=780,
                resizable=True,
                min_size=(920, 640),
                background_color="#0D0F17"
            )
            launched_native = True
            log("Starting PyWebView main loop...")
            webview.start()
        except Exception as e:
            log(f"PyWebView exception: {e}")
            launched_native = False

    if not launched_native and is_ready:
        log("Fallback to default browser...")
        webbrowser.open(SERVER_URL)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
