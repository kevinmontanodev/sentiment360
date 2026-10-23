import mongomock
import pytest

from pymongo.errors import DuplicateKeyError

from src.almacenamiento.repositorio_mongodb import MongoReviewRepository


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


def make_review(review_id: str, text: str = "Buena reseña") -> dict:
    return {
        "id": review_id,
        "text": text,
        "label": 4,
        "label_text": "4",
    }


def test_insert_reviews(repository):
    result = repository.insert_reviews([
        make_review("review-001"),
        make_review("review-002"),
    ])

    assert result == {"inserted": 2, "duplicates": 0}
    assert repository.count_reviews() == 2


def test_empty_batch(repository):
    result = repository.insert_reviews([])

    assert result == {"inserted": 0, "duplicates": 0}
    assert repository.count_reviews() == 0


def test_repeated_batch_does_not_duplicate(repository):
    reviews = [make_review("review-001")]

    first = repository.insert_reviews(reviews)
    second = repository.insert_reviews(reviews)

    assert first == {"inserted": 1, "duplicates": 0}
    assert second == {"inserted": 0, "duplicates": 1}
    assert repository.count_reviews() == 1


def test_duplicate_ids_inside_batch(repository):
    result = repository.insert_reviews([
        make_review("review-001", "Texto original"),
        make_review("review-001", "Texto diferente"),
    ])

    assert result == {"inserted": 1, "duplicates": 1}
    assert repository.count_reviews() == 1

    stored = repository._collection.find_one({"id": "review-001"})
    assert stored["text"] == "Texto original"


def test_existing_document_is_not_overwritten(repository):
    repository.insert_reviews([
        make_review("review-001", "Texto original")
    ])

    repository.insert_reviews([
        make_review("review-001", "Texto modificado")
    ])

    stored = repository._collection.find_one({"id": "review-001"})
    assert stored["text"] == "Texto original"


def test_unique_index_rejects_duplicate(repository):
    repository._collection.insert_one(make_review("review-001"))

    with pytest.raises(DuplicateKeyError):
        repository._collection.insert_one(make_review("review-001"))
