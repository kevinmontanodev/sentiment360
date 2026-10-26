from pathlib import Path

import boto3
from botocore.exceptions import ClientError


class S3ArtifactRepository:
    """Repositorio para guardar y recuperar artefactos en un bucket compatible con S3."""

    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        client=None,
    ) -> None:
        if not bucket.strip():
            raise ValueError("El nombre del bucket no puede estar vacío.")

        self.bucket = bucket
        self._client = client or boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        """Crea el bucket si todavía no existe."""
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self.bucket)

    def upload_file(self, local_path: Path, key: str) -> None:
        self._client.upload_file(str(local_path), self.bucket, key)

    def download_file(self, key: str, local_path: Path) -> None:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        self._client.download_file(self.bucket, key, str(local_path))

    def list_keys(self, prefix: str = "") -> list[str]:
        response = self._client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return sorted(item["Key"] for item in response.get("Contents", []))
