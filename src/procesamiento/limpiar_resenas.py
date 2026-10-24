"""Limpieza por lotes con Dask y salida Parquet validada."""

import json
import unicodedata
from collections.abc import Iterable, Mapping
from itertools import islice
from pathlib import Path
from tempfile import TemporaryDirectory

import dask
import dask.bag as db
import dask.dataframe as dd
import pandas as pd

from src.ingesta.validador import ReviewValidator


DTYPES = {"id": "string", "text": "string", "label": "int64", "label_text": "string"}


def clean_review(review: Mapping[str, object]) -> dict | None:
    """Rechaza registros inválidos y conserva ID y etiquetas originales."""
    try:
        ReviewValidator().validate(review)
    except (TypeError, ValueError):
        return None

    # Conserva tildes, negaciones, signos, mayúsculas y emojis.
    text = " ".join(unicodedata.normalize("NFC", review["text"]).split())
    if not text:
        return None

    return {
        "id": review["id"],
        "text": text,
        "label": review["label"],
        "label_text": review["label_text"],
    }


def validate_parquet(path: Path, expected_count: int) -> dict[str, int]:
    """Relee el Parquet con Dask y comprueba registros y etiquetas."""
    frame = dd.read_parquet(str(path / "*.parquet"), engine="pyarrow")
    if list(frame.columns) != list(DTYPES):
        raise ValueError("El Parquet no contiene las columnas esperadas.")

    invalid = (
        frame.isna().any(axis=1)
        | (frame["id"].str.strip().str.len() == 0)
        | (frame["text"].str.strip().str.len() == 0)
        | ~frame["label"].isin(range(5))
        | (frame["label_text"] != frame["label"].astype(str))
    )
    count, invalid_count, labels = dask.compute(
        frame.shape[0], invalid.sum(), frame["label"].value_counts(),
        scheduler="threads",
    )
    if count != expected_count or invalid_count:
        raise ValueError("El Parquet no cumple el conteo o el esquema esperado.")
    return {str(label): int(labels.get(label, 0)) for label in range(5)}


def process_reviews(
    reviews: Iterable[Mapping[str, object]],
    output_dir: str | Path,
    batch_size: int = 5000,
) -> dict:
    """Procesa un lote a la vez y publica la salida solo tras verificarla."""
    if batch_size <= 0:
        raise ValueError("El tamaño del lote debe ser mayor que cero.")

    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"La salida ya existe: {output}. Usa otro directorio.")
    output.parent.mkdir(parents=True, exist_ok=True)

    summary = {"read": 0, "kept": 0, "rejected": 0}
    expected_labels = {str(label): 0 for label in range(5)}
    iterator = iter(reviews)

    # Una ejecución fallida no deja un dataset parcial en el destino.
    with TemporaryDirectory(prefix=".procesamiento-", dir=output.parent) as temporary:
        staging = Path(temporary) / "reviews"
        staging.mkdir()
        part = 0

        while batch := list(islice(iterator, batch_size)):
            cleaned = db.from_sequence(
                batch, npartitions=min(4, len(batch))
            ).map(clean_review).compute(scheduler="threads")
            valid = [review for review in cleaned if review is not None]

            summary["read"] += len(batch)
            summary["kept"] += len(valid)
            summary["rejected"] += len(batch) - len(valid)
            for review in valid:
                expected_labels[str(review["label"])] += 1

            if valid:
                frame = pd.DataFrame(valid, columns=DTYPES).astype(DTYPES)
                frame.to_parquet(staging / f"part-{part:05d}.parquet", index=False)
                part += 1

        if part == 0:
            # Incluso una colección vacía produce un Parquet legible con esquema.
            pd.DataFrame(columns=DTYPES).astype(DTYPES).to_parquet(
                staging / "part-00000.parquet", index=False
            )

        labels = validate_parquet(staging, summary["kept"])
        if labels != expected_labels:
            raise ValueError("Las etiquetas guardadas no coinciden con las procesadas.")
        summary["labels"] = labels
        summary["parquet_verified"] = True
        (staging / "_resumen.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output)

    return summary
