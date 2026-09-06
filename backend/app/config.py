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
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'sih26034.db'}")

    # Storage
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", str(10 * 1024 * 1024))) # 10MB
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]

    # Compliance Engine: "mock" or "real"
    COMPLIANCE_ENGINE_TYPE: str = os.getenv("COMPLIANCE_ENGINE_TYPE", "mock")

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
