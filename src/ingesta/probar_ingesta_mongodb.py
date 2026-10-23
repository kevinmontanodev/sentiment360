from src.config import MongoSettings
from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.ingesta.servicio_ingesta import ReviewIngestionService
from src.ingesta.validador import ReviewValidator


def main() -> None:
    settings = MongoSettings.from_env()

    reviews = [
        {
            "id": "us02-prueba-001",
            "text": "El producto llegó en buen estado.",
            "label": 4,
            "label_text": "4",
        },
        {
            "id": "us02-prueba-002",
            "text": "La experiencia fue regular.",
            "label": 2,
            "label_text": "2",
        },
    ]

    with MongoReviewRepository(
        uri=settings.uri,
        database_name=settings.database,
        collection_name="reviews_us02_prueba",
    ) as repository:
        repository.ensure_indexes()

        service = ReviewIngestionService(
            validator=ReviewValidator(),
            repository=repository,
            batch_size=2,
        )

        print("Primera ingesta:")
        print(service.ingest(reviews))

        print("\nSegunda ingesta de las mismas reseñas:")
        print(service.ingest(reviews))


if __name__ == "__main__":
    main()
