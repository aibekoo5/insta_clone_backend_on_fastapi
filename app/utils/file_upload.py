import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

# Configure your upload path
UPLOAD_PATH = Path("static/uploads")
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

async def save_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Save uploaded file to local storage and return a URL path
    """
    try:
        # Create subfolder if specified
        save_path = UPLOAD_PATH / subfolder
        save_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = save_path / unique_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Return a URL path instead of system path
        return f"/static/uploads/{subfolder}/{unique_filename}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}"
        )

async def handle_file_upload(
    file: Optional[UploadFile],
    file_type: str  # 'image' or 'video'
) -> Optional[str]:
    """
    Handle file upload and validation
    """
    if file is None or not hasattr(file, 'filename') or not file.filename:
        return None

    # Validate file type
    if file_type == 'image' and not file.content_type.startswith("image/"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not an image"
        )
    elif file_type == 'video' and not file.content_type.startswith("video/"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a video"
        )

    # Save to local storage
    return await save_file(file, file_type + "s")

async def delete_file(file_path: str) -> bool:
    """
    Delete file from local storage if it exists
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        return False