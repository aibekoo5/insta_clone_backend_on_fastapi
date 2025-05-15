import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from fastapi import UploadFile, HTTPException, status
from app.config import settings
from urllib.parse import quote
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class S3UploadError(Exception):
    """Custom exception for S3 upload errors"""
    pass

def get_s3_client():
    """Initialize and return S3 client with proper configuration"""
    try:
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=boto3.session.Config(
                signature_version='s3v4',
                retries={'max_attempts': 3},
                connect_timeout=10,
                read_timeout=30
            )
        )
    except Exception as e:
        logger.error(f"S3 client initialization failed: {str(e)}")
        raise S3UploadError("Failed to initialize S3 client")


async def upload_file_to_s3(
        file: UploadFile,
        folder: str,
        make_public: bool = False,
        s3_client: Optional[any] = None
) -> str:

    client = s3_client or get_s3_client()

    try:
        # Validate input parameters
        if not file.filename or not file.content_type:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="File metadata is incomplete"
            )

        # Verify file size
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size > max_size_bytes:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB"
            )

        # Validate file type
        file_ext = file.filename.split('.')[-1].lower()
        if (file.content_type not in settings.ALLOWED_MIME_TYPES or
                file_ext not in settings.ALLOWED_MIME_TYPES[file.content_type]):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )

        # Generate secure filename
        filename = f"{folder}/{uuid.uuid4()}.{file_ext}"
        extra_args = {
            'ContentType': file.content_type,
            'Metadata': {
                'original-filename': file.filename,
                'upload-date': datetime.utcnow().isoformat(),
                'uploader-ip': 'X-Forwarded-For'  # Will be replaced with actual IP
            }
        }

        if make_public:
            extra_args['ACL'] = 'public-read'

        # Upload file
        await file.seek(0)
        client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            filename,
            ExtraArgs=extra_args
        )

        # Generate URL
        return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{quote(filename)}"

    except NoCredentialsError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not configured"
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"S3 operation failed: {error_code}")

        if error_code == 'AccessDenied':
            detail = "Permission denied for S3 operation"
        elif error_code == 'NoSuchBucket':
            detail = "Specified bucket does not exist"
        else:
            detail = f"S3 service error: {error_code}"

        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=detail)
    except EndpointConnectionError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to storage service"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected upload error")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )
    finally:
        await file.close()


async def delete_file_from_s3(file_url: str) -> bool:
    client = get_s3_client()

    try:
        # Extract bucket and key from URL
        if not file_url.startswith(f"https://{settings.S3_BUCKET_NAME}.s3."):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Invalid S3 file URL format"
            )

        key = file_url.split(f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
        key = key.split('?')[0]  # Remove query params if presigned URL

        # Verify the key exists in the expected path
        if not key.startswith(('uploads/', 'posts/', 'temp-uploads/')):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Can only delete files from allowed paths"
            )

        # Delete the file
        client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key
        )

        logger.info(f"Deleted file: {key}")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'NoSuchKey':
            logger.warning(f"File not found: {key}")
            return False
        elif error_code == 'AccessDenied':
            logger.error(f"Delete permission denied for {key}")
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Delete operation not permitted"
            )
        else:
            logger.error(f"S3 delete failed: {error_code}")
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail="Storage service error"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected delete error")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File deletion failed"
        )