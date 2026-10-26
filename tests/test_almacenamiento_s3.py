import boto3
import pandas as pd
import pytest
from moto import mock_aws

from src.almacenamiento.repositorio_objetos import S3ArtifactRepository
from src.almacenamiento.transferir_artefacto import transfer, verify
from src.config import S3Settings

BUCKET = "sentiment360-test"


@pytest.fixture
def repository():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        yield S3ArtifactRepository(bucket=BUCKET, client=client)


@pytest.fixture
def parquet_dir(tmp_path):
    """Imita la salida de la US-03: un directorio Parquet con su resumen."""
    source = tmp_path / "reviews"
    source.mkdir()
    pd.DataFrame(
        {"id": ["r1", "r2"], "text": ["Muy bueno", "Malo"], "label": [4, 0], "label_text": ["4", "0"]}
    ).to_parquet(source / "part-00000.parquet", index=False)
    (source / "_resumen.json").write_text('{"read": 2}', encoding="utf-8")
    return source


def test_settings_require_all_variables(monkeypatch):
    monkeypatch.setattr("src.config.load_dotenv", lambda: None)
    for name in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValueError, match="S3_BUCKET"):
        S3Settings.from_env()


def test_ensure_bucket_can_run_twice(repository):
    repository.ensure_bucket()
    repository.ensure_bucket()
    assert repository.list_keys() == []


def test_transfer_uploads_and_recovers_identical_parquet(repository, parquet_dir, tmp_path):
    destination = tmp_path / "recovered"

    summary = transfer(repository, parquet_dir, destination, "reviews")

    assert summary["keys"] == ["reviews/_resumen.json", "reviews/part-00000.parquet"]
    assert summary["files"] == 2
    assert summary["rows"] == 2
    assert summary["verified"] is True
    pd.testing.assert_frame_equal(pd.read_parquet(parquet_dir), pd.read_parquet(destination))


def test_verify_detects_modified_file(parquet_dir, tmp_path):
    copy = tmp_path / "copy"
    copy.mkdir()
    (copy / "_resumen.json").write_text('{"read": 2}', encoding="utf-8")
    pd.DataFrame({"id": ["otro"]}).to_parquet(copy / "part-00000.parquet", index=False)

    with pytest.raises(AssertionError, match="part-00000.parquet"):
        verify(parquet_dir, copy)
