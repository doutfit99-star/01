# -*- coding: utf-8 -*-
"""
DH DOW - Build Standalone Windows Executable
Packages Python backend, you_get engine, yt_dlp engine, and static assets into dist/DH-DOW.exe.
"""

import os
import sys
import subprocess
from pathlib import Path

def build():
    print("=" * 60)
    print("         DH DOW - BUILDING STANDALONE WIN32 EXE         ")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=DH-DOW",
        "--onefile",
        "--noconsole",
        "--clean",
        "--noconfirm",
        "--add-data=static;static",
        "--add-data=you_get;you_get",
        "--add-data=yt_dlp;yt_dlp",
        "--collect-all=yt_dlp",
        "--collect-all=you_get",
        "--collect-all=uvicorn",
        "--collect-all=fastapi",
        "app.py"
    ]

    print(f"[*] Running PyInstaller build: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_path = Path("dist") / "DH-DOW.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"[SUCCESS] Exported standalone executable: DH-DOW.exe ({size_mb:.1f} MB)")
            print(f"Path: {exe_path.resolve()}")
            print("=" * 60)
        else:
            print("\n[SUCCESS] Build finished successfully.")
    else:
        print("\n[ERROR] Build failed during PyInstaller step.")

if __name__ == "__main__":
    build()
