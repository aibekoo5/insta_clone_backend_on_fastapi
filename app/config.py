from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import ClassVar, Dict, List, Optional

load_dotenv()


class Settings(BaseSettings):
    # App Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30


    # Database
    DATABASE_URL: str

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: Optional[str] = None

    # File Upload Constraints
    MAX_FILE_SIZE_MB: int = 10

    # Class variables (not settings fields)
    ALLOWED_MIME_TYPES: ClassVar[Dict[str, List[str]]] = {
        "image/jpeg": ["jpg", "jpeg"],
        "image/png": ["png"],
        "image/gif": ["gif"],
        "image/webp": ["webp"],
        "image/avif": ["avif"],
        "video/mp4": ["mp4"],
        "video/webm": ["webm"],
        "video/ogg": ["ogg"],
    }
    ALLOWED_IMAGE_EXTENSIONS: ClassVar[List[str]] = ["jpg", "jpeg", "png", "gif"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()