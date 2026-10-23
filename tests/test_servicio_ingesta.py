import mongomock
import pytest

from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.ingesta.servicio_ingesta import ReviewIngestionService
from src.ingesta.validador import ReviewValidator


@pytest.fixture
def repository():
    collection = mongomock.MongoClient().sentiment360.reviews
    repo = MongoReviewRepository(
        uri="",
        database_name="",
        collection=collection,
    )
    repo.ensure_indexes()

    yield repo
    repo.close()


@pytest.fixture
def service(repository):
    return ReviewIngestionService(
        validator=ReviewValidator(),
        repository=repository,
        batch_size=2,
    )


def make_review(review_id, text="Buena reseña", label=4):
    return {
        "id": review_id,
        "text": text,
        "label": label,
        "label_text": str(label),
    }


def test_ingest_valid_reviews(service):
    result = service.ingest([
        make_review("r1"),
        make_review("r2"),
    ])

    assert result == {
        "received": 2,
        "inserted": 2,
        "duplicates": 0,
        "rejected": 0,
        "stored_total": 2,
    }


def test_reject_invalid_reviews(service):
    result = service.ingest([
        make_review("r1"),
        make_review("r2", text="   "),
        make_review("r3", label=7),
    ])

    assert result == {
        "received": 3,
        "inserted": 1,
        "duplicates": 0,
        "rejected": 2,
        "stored_total": 1,
    }


def test_repeated_ingestion_is_idempotent(service):
    reviews = [
        make_review("r1"),
        make_review("r2"),
    ]

    first = service.ingest(reviews)
    second = service.ingest(reviews)

    assert first["inserted"] == 2
    assert second["inserted"] == 0
    assert second["duplicates"] == 2
    assert second["stored_total"] == 2


def test_empty_ingestion(service):
    result = service.ingest([])

    assert result == {
        "received": 0,
        "inserted": 0,
        "duplicates": 0,
        "rejected": 0,
        "stored_total": 0,
    }


def test_invalid_batch_size(repository):
    with pytest.raises(ValueError):
        ReviewIngestionService(
            validator=ReviewValidator(),
            repository=repository,
            batch_size=0,
        )


def test_invalid_review_does_not_reach_mongodb(service, repository):
    service.ingest([
        make_review("r1", text=""),
    ])

    assert repository.count_reviews() == 0
