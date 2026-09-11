import os
from pathlib import Path
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    BaseSettings = object  # Fallback

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    APP_NAME: str = "SIH26034 Packaged Commodity Compliance Screening API"

    def __init__(self):
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.HOST: str = os.getenv("HOST", "0.0.0.0")

        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'sih26034.db'}")

        # Storage
        self.UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
        self.MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10MB
        self.ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

        # CORS
        raw_origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
        )
        self.ALLOWED_ORIGINS: List[str] = [
            origin.strip()
            for origin in raw_origins.split(",")
            if origin.strip()
        ]

        # Compliance Engine: "mock" or "real" (Defaults to "real" for live API mode)
        self.COMPLIANCE_ENGINE_TYPE: str = os.getenv("COMPLIANCE_ENGINE_TYPE", "real")

        # Frontend Serving (Unified Full-Stack Deployment)
        self.SERVE_FRONTEND: bool = os.getenv("SERVE_FRONTEND", "true").lower() in ("true", "1", "yes")

    @property
    def FRONTEND_DIR(self) -> Path:
        custom_dir = os.getenv("FRONTEND_DIR")
        if custom_dir:
            return Path(custom_dir).resolve()
        # Check standard relative locations
        parent_frontend = (BASE_DIR.parent / "frontend").resolve()
        if parent_frontend.exists():
            return parent_frontend
        local_frontend = (BASE_DIR / "frontend").resolve()
        if local_frontend.exists():
            return local_frontend
        return parent_frontend

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
