from collections.abc import Iterable, Mapping
from typing import Any

from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.ingesta.validador import ReviewValidator


class ReviewIngestionService:
    """Coordina la validación y persistencia de reseñas."""

    def __init__(
        self,
        validator: ReviewValidator,
        repository: MongoReviewRepository,
        batch_size: int = 500,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size debe ser mayor que cero.")

        self._validator = validator
        self._repository = repository
        self._batch_size = batch_size

    def ingest(
        self,
        reviews: Iterable[Mapping[str, Any]],
    ) -> dict[str, int]:
        """Valida e inserta reseñas en lotes.

        Las reseñas inválidas se rechazan. Los errores de infraestructura
        se propagan para no informar una ingesta exitosa falsamente.
        """
        received = 0
        rejected = 0
        inserted = 0
        duplicates = 0
        valid_batch: list[Mapping[str, Any]] = []

        def persist_batch() -> None:
            nonlocal inserted, duplicates

            if not valid_batch:
                return

            result = self._repository.insert_reviews(valid_batch)
            inserted += result["inserted"]
            duplicates += result["duplicates"]
            valid_batch.clear()

        for review in reviews:
            received += 1

            try:
                self._validator.validate(review)
            except (TypeError, ValueError):
                rejected += 1
                continue

            valid_batch.append(review)

            if len(valid_batch) >= self._batch_size:
                persist_batch()

        persist_batch()

        return {
            "received": received,
            "inserted": inserted,
            "duplicates": duplicates,
            "rejected": rejected,
            "stored_total": self._repository.count_reviews(),
        }
