# -*- coding: utf-8 -*-
"""
Vercel Serverless Entrypoint for DH DOW Web Application
"""

import os
import sys
from pathlib import Path

# Add root directory to sys.path so server.py and engine.py can be imported
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from server import app

# Export FastAPI app for Vercel Serverless Functions
app = app
handler = app
