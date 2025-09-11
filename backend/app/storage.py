# backend/app/storage.py
from __future__ import annotations
import datetime as dt
from typing import Optional
import boto3
from botocore.client import Config
from .config import settings

class S3Storage:
    def __init__(
        self,
        region: str,
        bucket: str,
        prefix: str = "",
        profile: Optional[str] = None,
        kms_key_id: Optional[str] = None,
    ):
        self.region = region
        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/" if prefix and not prefix.endswith("/") else (prefix or "")
        self.kms_key_id = kms_key_id

        session = boto3.session.Session(profile_name=profile) if profile else boto3.session.Session()
        # Use signature v4 w/ TLS; Supplied region controls endpoint form
        self.client = session.client("s3", region_name=region, config=Config(s3={"addressing_style": "virtual"}))

    def _full_key(self, key: str) -> str:
        return f"{self.prefix}{key}" if self.prefix else key

    def put_text(self, key: str, text: str) -> str:
        params = {
            "Bucket": self.bucket,
            "Key": self._full_key(key),
            "Body": text.encode("utf-8"),
        }
        # Default server-side encryption
        if self.kms_key_id:
            params["ServerSideEncryption"] = "aws:kms"
            params["SSEKMSKeyId"] = self.kms_key_id
        else:
            params["ServerSideEncryption"] = "AES256"

        self.client.put_object(**params)
        return params["Key"]

    def public_url(self, key: str) -> str:
        # For private buckets this won’t be directly accessible without a signed URL.
        key = self._full_key(key)
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

def build_essay_key(asurite: str, session_id: str) -> str:
    d = dt.datetime.utcnow().strftime("%Y/%m/%d")
    # e.g. writing-feedback/essays/2025/09/11/abc123/<uuid>.txt
    safe_asurite = (asurite or "unknown").strip().lower()
    return f"essays/{d}/{safe_asurite}/{session_id}.txt"

# Lazy singleton accessor
_s3: Optional[S3Storage] = None
def get_storage() -> Optional[S3Storage]:
    global _s3
    if _s3 is not None:
        return _s3
    if not (settings.STORE_ESSAY_S3 and settings.AWS_REGION and settings.AWS_S3_BUCKET):
        _s3 = None
        return None
    _s3 = S3Storage(
        region=settings.AWS_REGION,
        bucket=settings.AWS_S3_BUCKET,
        prefix=settings.AWS_S3_PREFIX,
        profile=settings.AWS_PROFILE,
        kms_key_id=settings.AWS_KMS_KEY_ID,
    )
    return _s3
