from collections.abc import Mapping, Sequence
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError


class MongoReviewRepository:
    """Repositorio para almacenar reseñas originales en MongoDB."""

    def __init__(
        self,
        uri: str,
        database_name: str,
        collection_name: str = "reviews",
        collection: Collection | None = None,
    ) -> None:
        if collection is not None:
            self._client = None
            self._collection = collection
        else:
            if not uri.strip():
                raise ValueError("La URI de MongoDB no puede estar vacía.")

            if not database_name.strip():
                raise ValueError("El nombre de la base de datos no puede estar vacío.")

            self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self._collection = self._client[database_name][collection_name]

    def ensure_indexes(self) -> None:
        """Garantiza que cada reseña tenga un ID único."""
        self._collection.create_index(
            [("id", ASCENDING)],
            unique=True,
            name="uq_review_id",
        )

    def insert_reviews(
        self,
        reviews: Sequence[Mapping[str, Any]],
    ) -> dict[str, int]:
        """Inserta reseñas sin reemplazar documentos existentes.

        Los documentos con ID repetido se contabilizan como duplicados.
        Los demás errores de escritura se propagan.
        """
        if not reviews:
            return {"inserted": 0, "duplicates": 0}

        # Evita intentar insertar varias veces el mismo ID en un lote.
        unique_reviews: list[Mapping[str, Any]] = []
        seen_ids: set[str] = set()
        duplicates = 0

        for review in reviews:
            review_id = review.get("id")

            if isinstance(review_id, str) and review_id in seen_ids:
                duplicates += 1
                continue

            if isinstance(review_id, str):
                seen_ids.add(review_id)

            unique_reviews.append(review)

        try:
            result = self._collection.insert_many(
                [dict(review) for review in unique_reviews],
                ordered=False,
            )
            inserted = len(result.inserted_ids)

        except BulkWriteError as exc:
            details = exc.details or {}
            write_errors = details.get("writeErrors", [])

            duplicate_errors = [
                error for error in write_errors
                if error.get("code") == 11000
            ]
            other_errors = [
                error for error in write_errors
                if error.get("code") != 11000
            ]

            if other_errors or details.get("writeConcernErrors"):
                raise

            inserted = details.get("nInserted", 0)
            duplicates += len(duplicate_errors)

        return {
            "inserted": inserted,
            "duplicates": duplicates,
        }

    def count_reviews(self) -> int:
        """Devuelve el total de reseñas almacenadas."""
        return self._collection.count_documents({})

    def close(self) -> None:
        """Cierra la conexión si el repositorio la creó."""
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> "MongoReviewRepository":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
