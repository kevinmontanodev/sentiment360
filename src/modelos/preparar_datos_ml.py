"""Obtiene una revisión fija del corpus y prepara la evaluación complementaria."""

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.modelos.texto import normalize_text
from src.procesamiento.limpiar_resenas import process_reviews


DATASET = "SetFit/amazon_reviews_multi_es"
REVISION = "16015418b488c9186fce74b058877ea939ca934d"


def filter_evaluation(train, validation, test):
    """Prioriza train y luego validation; no altera etiquetas ni train."""
    train_keys = set(train["text"].map(normalize_text))
    validation_keys = set(validation["text"].map(normalize_text))
    validation_mask = ~validation["text"].map(normalize_text).isin(train_keys)
    test_mask = ~test["text"].map(normalize_text).isin(train_keys | validation_keys)
    validation_mask &= ~validation["id"].isin(train["id"])
    test_mask &= ~test["id"].isin(set(train["id"]) | set(validation["id"]))
    return validation[validation_mask].copy(), test[test_mask].copy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara train, validation y test para ML.")
    parser.add_argument("--raw", type=Path, default=Path("data/raw/amazon_reviews_multi_es") / REVISION)
    parser.add_argument("--output", type=Path, default=Path("data/processed/ml"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("La salida ya existe; elige un directorio nuevo.")
    args.raw.mkdir(parents=True, exist_ok=True)
    source = {"dataset": DATASET, "revision": REVISION, "files": {}, "cleaning": {}}
    for split in ("train", "validation", "test"):
        raw_file = args.raw / f"{split}.jsonl"
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{split}.jsonl"
        if not raw_file.exists():
            print(f"Descargando {split}...", flush=True)
            temporary = raw_file.with_suffix(".download")
            with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as target:
                shutil.copyfileobj(response, target)
            temporary.replace(raw_file)
        source["files"][split] = {
            "url": url, "sha256": hashlib.sha256(raw_file.read_bytes()).hexdigest(),
        }

        def reviews():
            with raw_file.open(encoding="utf-8") as stream:
                for line in stream:
                    yield json.loads(line)

        # Verifica en la carpeta temporal del sistema antes de copiar a OneDrive.
        # Algunas carpetas sincronizadas bloquean el renombrado de directorios abiertos.
        with TemporaryDirectory(prefix="sentiment360-ml-") as temporary:
            cleaned = Path(temporary) / split
            source["cleaning"][split] = process_reviews(reviews(), cleaned)
            shutil.copytree(cleaned, args.output / "original" / split)

    train, validation, test = [pd.read_parquet(args.output / "original" / split)
                                for split in ("train", "validation", "test")]
    filtered_validation, filtered_test = filter_evaluation(train, validation, test)
    for split, frame in (("train", train), ("validation", filtered_validation), ("test", filtered_test)):
        frame.to_parquet(args.output / f"{split}.parquet", index=False)
    source["evaluation"] = {
        "train": len(train), "validation": len(filtered_validation), "test": len(filtered_test),
        "removed_validation": len(validation) - len(filtered_validation),
        "removed_test": len(test) - len(filtered_test),
        "matching": "NFC, casefold y espacios normalizados; también se excluyen IDs compartidos",
    }
    (args.output / "_source.json").write_text(
        json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(source["evaluation"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
