import json
import sys

import mongomock
import pandas as pd
import pytest

from src.almacenamiento.repositorio_mongodb import MongoReviewRepository
from src.procesamiento import procesar_resenas
from src.procesamiento.limpiar_resenas import clean_review, process_reviews, validate_parquet


def make_review(review_id="review-1", label=4, text="  ¡NO está mal!\nMuy útil 😊  "):
    return {"id": review_id, "text": text, "label": label, "label_text": str(label)}


def test_cleaning_preserves_sentiment_and_original_fields():
    review = make_review(text="  ¡NO esta\u0301 mal!\tMuy\n útil 😊  ")
    original = dict(review)

    assert clean_review(review) == {
        "id": "review-1", "text": "¡NO está mal! Muy útil 😊",
        "label": 4, "label_text": "4",
    }
    assert review == original


@pytest.mark.parametrize("changes", [
    {"id": None}, {"id": " "}, {"text": None}, {"text": 123},
    {"text": "\n\t "}, {"label": None}, {"label": True},
    {"label": 4.0}, {"label": "4"}, {"label": -1}, {"label": 5},
    {"label_text": None}, {"label_text": "3"},
])
def test_invalid_fields_are_rejected(changes):
    assert clean_review(make_review() | changes) is None


@pytest.mark.parametrize("review", [None, [], {}, {"id": "missing-fields"}])
def test_invalid_or_missing_records_are_rejected(review):
    assert clean_review(review) is None


def test_mongodb_to_parquet_in_batches(tmp_path):
    collection = mongomock.MongoClient().sentiment360.reviews
    documents = [make_review(f"review-{label}", label) for label in range(5)]
    documents += [make_review("null", text=None), {"id": "missing"}]
    collection.insert_many(documents)
    original = list(collection.find())
    output = tmp_path / "reviews"

    with MongoReviewRepository("", "", collection=collection) as repository:
        summary = process_reviews(repository.iter_reviews(2), output, batch_size=2)

    assert summary == {
        "read": 7, "kept": 5, "rejected": 2,
        "labels": {str(label): 1 for label in range(5)},
        "parquet_verified": True,
    }
    assert json.loads((output / "_resumen.json").read_text()) == summary
    saved = pd.read_parquet(output).sort_values("id")
    assert saved["id"].tolist() == [f"review-{label}" for label in range(5)]
    assert saved["label"].tolist() == list(range(5))
    assert saved["label_text"].tolist() == list("01234")
    assert saved["text"].tolist() == ["¡NO está mal! Muy útil 😊"] * 5
    assert list(saved.columns) == ["id", "text", "label", "label_text"]
    assert len(list(output.glob("*.parquet"))) == 3
    assert list(collection.find()) == original


@pytest.mark.parametrize("reviews", [[], [make_review(text=None)]])
def test_empty_or_all_rejected_input_produces_readable_parquet(tmp_path, reviews):
    summary = process_reviews(reviews, tmp_path / "reviews")
    assert summary["read"] == summary["rejected"] == len(reviews)
    assert summary["kept"] == 0
    assert pd.read_parquet(tmp_path / "reviews").empty


def test_existing_output_is_preserved(tmp_path):
    output = tmp_path / "reviews"
    process_reviews([make_review()], output)
    original = (output / "part-00000.parquet").read_bytes()
    with pytest.raises(FileExistsError):
        process_reviews([make_review("different")], output)
    assert (output / "part-00000.parquet").read_bytes() == original


def test_source_failure_leaves_no_partial_output(tmp_path):
    def failing_source():
        yield make_review()
        raise RuntimeError("Lectura interrumpida")

    with pytest.raises(RuntimeError, match="Lectura interrumpida"):
        process_reviews(failing_source(), tmp_path / "reviews", batch_size=1)
    assert list(tmp_path.iterdir()) == []


def test_parquet_validation_rejects_wrong_counts_and_labels(tmp_path):
    output = tmp_path / "reviews"
    process_reviews([make_review()], output)
    with pytest.raises(ValueError):
        validate_parquet(output, expected_count=2)
    frame = pd.read_parquet(output)
    frame["label"] = 9
    frame.to_parquet(output / "part-00000.parquet", index=False)
    with pytest.raises(ValueError):
        validate_parquet(output, expected_count=1)


@pytest.mark.parametrize("batch_size", [0, -1])
def test_invalid_batch_size(tmp_path, batch_size):
    with pytest.raises(ValueError):
        process_reviews([], tmp_path / "reviews", batch_size=batch_size)
    with MongoReviewRepository("", "", collection=mongomock.MongoClient().db.reviews) as repo:
        with pytest.raises(ValueError):
            list(repo.iter_reviews(batch_size))


def test_cli_reads_selected_collection_and_respects_limit(tmp_path, monkeypatch, capsys):
    client = mongomock.MongoClient()
    client.db.sample.insert_many([make_review("one"), make_review("two")])
    output = tmp_path / "sample"
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "db")

    def repository(uri, database_name, collection_name):
        assert database_name == "db"
        assert collection_name == "sample"
        return MongoReviewRepository("", "", collection=client[database_name][collection_name])

    monkeypatch.setattr(procesar_resenas, "MongoReviewRepository", repository)
    monkeypatch.setattr(sys, "argv", [
        "procesar_resenas", "--collection", "sample", "--limit", "1",
        "--batch-size", "1", "--output", str(output),
    ])
    procesar_resenas.main()

    assert pd.read_parquet(output)["id"].tolist() == ["one"]
    assert '"read": 1' in capsys.readouterr().out
