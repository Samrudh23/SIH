#!/usr/bin/env python3
"""
SIH26034 — Packaged Commodity Compliance Scanner
Production Server Launcher
"""

import os
import sys
from pathlib import Path

# Ensure repo root and backend directory are on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(1, str(REPO_ROOT))

# Load optional .env file if present
try:
    from dotenv import load_dotenv
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

import uvicorn
from app.config import settings
from app.database.session import init_db

def main():
    print("=" * 68)
    print("SIH26034 Legal Metrology Packaged Commodities Compliance Scanner")
    print("Production Server Initializing...")
    print("=" * 68)

    # 1. Initialize Database Tables
    print(f"[*] Database URL:    {settings.DATABASE_URL}")
    init_db()
    print("[+] Database initialized successfully.")

    # 2. Verify Storage Directory
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[+] Storage Uploads: {settings.UPLOAD_DIR.resolve()}")

    # 3. Check Frontend Integration
    if settings.SERVE_FRONTEND and settings.FRONTEND_DIR.exists():
        print(f"[+] Unified Frontend: Mounted from {settings.FRONTEND_DIR.resolve()}")
    else:
        print("[!] Unified Frontend: Disabled (Decoupled API-only mode)")

    host = settings.HOST
    port = settings.PORT
    workers = int(os.getenv("WEB_CONCURRENCY", "1" if os.name == "nt" else "2"))

    print("\n" + "-" * 68)
    print(f"Server binding to:   http://{host}:{port}")
    print(f"Inspector UI Portal: http://localhost:{port}/")
    print(f"API Health Endpoint: http://localhost:{port}/api/health")
    print(f"OpenAPI Interactive: http://localhost:{port}/docs")
    print("-" * 68 + "\n")

    # On Windows, multiple workers with Uvicorn require specific process spawning,
    # so we default to 1 worker on Windows development/demo runs or use WEB_CONCURRENCY.
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=workers if os.name != "nt" else 1,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()
