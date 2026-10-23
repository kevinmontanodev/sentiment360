import argparse

from datasets import load_dataset

from src.config import MongoSettings
from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.ingesta.servicio_ingesta import ReviewIngestionService
from src.ingesta.validador import ReviewValidator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Carga reseñas de Amazon en MongoDB."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Máximo de reseñas que leer. Omítelo para procesar todo train.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Número de reseñas válidas por lote.",
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="Colección destino; por defecto usa la configurada.",
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit debe ser mayor que cero.")

    if args.batch_size <= 0:
        parser.error("--batch-size debe ser mayor que cero.")

    settings = MongoSettings.from_env()

    dataset = load_dataset(
        "SetFit/amazon_reviews_multi_es",
        split="train",
        streaming=True,
    )

    if args.limit is not None:
        dataset = dataset.take(args.limit)

    with MongoReviewRepository(
        uri=settings.uri,
        database_name=settings.database,
        collection_name=args.collection or settings.collection,
    ) as repository:
        repository.ensure_indexes()

        service = ReviewIngestionService(
            validator=ReviewValidator(),
            repository=repository,
            batch_size=args.batch_size,
        )

        result = service.ingest(dataset)

    print("\nResumen de ingesta")
    print("------------------")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
