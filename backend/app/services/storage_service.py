import os
import uuid
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException

from app.config import settings

class BaseStorageService(ABC):
    @abstractmethod
    async def save_image(self, file: UploadFile, inspection_id: str) -> Tuple[str, str, int, str]:
        """
        Saves an uploaded image.
        Returns: (evidence_id, safe_file_name, file_size_bytes, mime_type)
        """
        pass

    @abstractmethod
    def get_file_path(self, file_name: str) -> Path:
        """Returns the absolute filesystem path for a stored file."""
        pass

    @abstractmethod
    def delete_file(self, file_name: str) -> bool:
        """Deletes a stored file."""
        pass

class LocalStorageService(BaseStorageService):
    def __init__(self, upload_dir: Path = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file: UploadFile, inspection_id: str) -> Tuple[str, str, int, str]:
        # 1. Validate file presence
        if not file.filename:
            raise HTTPException(status_code=400, detail="Empty filename provided.")

        # 2. Extract and validate extension
        raw_ext = Path(file.filename).suffix.lower()
        if raw_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension '{raw_ext}'. Allowed: {', '.join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS))}"
            )

        # 3. Read content and validate file size
        content = await file.read()
        file_size = len(content)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )

        # 4. Determine MIME type
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "image/jpeg"

        # 5. Generate secure unique filename and evidence ID (UUID)
        evidence_id = str(uuid.uuid4())
        safe_file_name = f"{inspection_id}_{evidence_id}{raw_ext}"
        target_path = (self.upload_dir / safe_file_name).resolve()

        # Path traversal guard
        if not str(target_path).startswith(str(self.upload_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file destination path.")

        # 6. Save bytes to local storage
        with open(target_path, "wb") as f:
            f.write(content)

        return evidence_id, safe_file_name, file_size, mime_type

    def get_file_path(self, file_name: str) -> Path:
        # Strip any directory components from client to prevent traversal
        sanitized_name = Path(file_name).name
        resolved_path = (self.upload_dir / sanitized_name).resolve()
        if not str(resolved_path).startswith(str(self.upload_dir.resolve())):
            raise HTTPException(status_code=400, detail="Access denied.")
        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{sanitized_name}' not found.")
        return resolved_path

    def delete_file(self, file_name: str) -> bool:
        try:
            path = self.get_file_path(file_name)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

# Global singleton instance
storage_service = LocalStorageService()
