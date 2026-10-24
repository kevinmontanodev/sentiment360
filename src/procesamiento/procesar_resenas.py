"""Ejecutar desde la raíz: python -m src.procesamiento.procesar_resenas."""

import argparse
import json
from contextlib import closing
from itertools import islice
from pathlib import Path

from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.config import MongoSettings
from src.procesamiento.limpiar_resenas import process_reviews


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpia reseñas de MongoDB con Dask.")
    parser.add_argument("--collection", default=None, help="Colección origen; por defecto reviews.")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--limit", type=int, default=None, help="Limitar la lectura para pruebas.")
    parser.add_argument("--output", type=Path, default=Path("data/processed/reviews"))
    args = parser.parse_args()

    if args.batch_size <= 0:
        parser.error("--batch-size debe ser mayor que cero.")
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit debe ser mayor que cero.")
    if args.output.exists():
        parser.error("La salida ya existe. Usa --output con otro directorio.")

    settings = MongoSettings.from_env()
    with MongoReviewRepository(
        uri=settings.uri,
        database_name=settings.database,
        collection_name=args.collection or settings.collection,
    ) as repository:
        with closing(repository.iter_reviews(args.batch_size)) as cursor:
            reviews = islice(cursor, args.limit) if args.limit is not None else cursor
            summary = process_reviews(reviews, args.output, args.batch_size)

    print("Resumen de procesamiento")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Salida: {args.output}")


if __name__ == "__main__":
    main()
