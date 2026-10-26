"""Ejecutar desde la raíz: python -m src.almacenamiento.transferir_artefacto."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from src.almacenamiento.repositorio_objetos import S3ArtifactRepository
from src.config import S3Settings


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def list_files(directory: Path) -> list[Path]:
    """Devuelve los archivos del directorio como rutas relativas y ordenadas."""
    return sorted(p.relative_to(directory) for p in directory.rglob("*") if p.is_file())


def upload_directory(repository: S3ArtifactRepository, source: Path, prefix: str) -> list[str]:
    keys = []
    for relative in list_files(source):
        key = f"{prefix}/{relative.as_posix()}"
        repository.upload_file(source / relative, key)
        keys.append(key)
    return keys


def download_prefix(repository: S3ArtifactRepository, prefix: str, destination: Path) -> None:
    for key in repository.list_keys(prefix + "/"):
        repository.download_file(key, destination / key[len(prefix) + 1:])


def verify(source: Path, destination: Path) -> dict:
    """Comprueba que la copia recuperada sea idéntica y legible como Parquet."""
    source_files = list_files(source)
    if source_files != list_files(destination):
        raise AssertionError("Los archivos recuperados no coinciden con los originales.")

    for relative in source_files:
        if sha256(source / relative) != sha256(destination / relative):
            raise AssertionError(f"El contenido de {relative} no coincide.")

    original = pd.read_parquet(source)
    recovered = pd.read_parquet(destination)
    pd.testing.assert_frame_equal(original, recovered)

    return {"files": len(source_files), "rows": len(recovered), "verified": True}


def transfer(
    repository: S3ArtifactRepository, source: Path, destination: Path, prefix: str
) -> dict:
    repository.ensure_bucket()
    keys = upload_directory(repository, source, prefix)
    download_prefix(repository, prefix, destination)
    summary = verify(source, destination)
    return {"bucket": repository.bucket, "keys": keys, **summary}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sube y recupera un artefacto Parquet en MinIO.")
    parser.add_argument("--source", type=Path, default=Path("data/processed/reviews"))
    parser.add_argument("--destination", type=Path, default=Path("data/recovered/reviews"))
    parser.add_argument("--prefix", default="reviews")
    args = parser.parse_args()

    if not args.source.is_dir():
        parser.error("No existe el artefacto de origen. Ejecuta primero el procesamiento (US-03).")
    if args.destination.exists():
        parser.error("El destino ya existe. Usa --destination con otro directorio.")

    settings = S3Settings.from_env()
    repository = S3ArtifactRepository(
        bucket=settings.bucket,
        endpoint_url=settings.endpoint_url,
        access_key=settings.access_key,
        secret_key=settings.secret_key,
    )
    summary = transfer(repository, args.source, args.destination, args.prefix.strip("/"))

    print("Resumen de almacenamiento")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
