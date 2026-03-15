import io
import uuid
from typing import Tuple
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class MinioService:
    """MinIO object storage client — wraps presigned URL generation and object download."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,  # TLS terminated at ingress in production
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            raise RuntimeError(f"MinIO bucket init failed: {e}") from e

    async def generate_presigned_put(
        self, project_id: str, filename: str, content_type: str
    ) -> Tuple[str, str, str]:
        """
        Returns (document_id, signed_put_url, minio_object_key).
        URL is valid for 15 minutes.
        """
        document_id = str(uuid.uuid4())
        safe_name = filename.replace(" ", "_")
        minio_key = f"{project_id}/{document_id}/{safe_name}"
        from datetime import timedelta
        signed_url = self.client.presigned_put_object(
            settings.MINIO_BUCKET, minio_key, expires=timedelta(minutes=15)
        )
        return document_id, signed_url, minio_key

    async def download_object(self, minio_key: str) -> bytes:
        """Download object from MinIO and return as bytes."""
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, minio_key)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise RuntimeError(f"MinIO download failed for key '{minio_key}': {e}") from e
