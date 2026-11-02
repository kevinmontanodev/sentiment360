import json
import subprocess
import sys

import joblib
import numpy as np
import pandas as pd
import pytest

from src.modelos.comparar_ml import (
    compare_models, dataset_fingerprint, normalize_text, read_reviews, split_reviews,
)
from src.modelos.preparar_datos_ml import filter_evaluation


def reviews(count=15, prefix="review"):
    words = ["terrible", "malo", "regular", "bueno", "excelente"]
    return pd.DataFrame([
        {"id": f"{prefix}-{label}-{index}", "text": f"{words[label]} producto {prefix} caso{index}",
         "label": label} for label in range(5) for index in range(count)
    ])


def test_split_keeps_normalized_duplicates_together_and_five_labels():
    frame = reviews(30)
    duplicate = frame.copy()
    duplicate["id"] += "-copy"
    duplicate["text"] = duplicate["text"].str.upper() + "  "
    frame = pd.concat([frame, duplicate], ignore_index=True)
    train, test = split_reviews(frame)
    assert not set(train["id"]) & set(test["id"])
    assert not set(train["text"].map(normalize_text)) & set(test["text"].map(normalize_text))
    assert set(train["label"]) == set(test["label"]) == set(range(5))
    assert len(train) + len(test) == len(frame)
    assert 0.15 <= len(test) / len(frame) <= 0.25
    repeated_train, repeated_test = split_reviews(frame)
    assert dataset_fingerprint(train) == dataset_fingerprint(repeated_train)
    assert dataset_fingerprint(test) == dataset_fingerprint(repeated_test)


def test_filter_removes_duplicates_from_original_validation_as_well():
    train = reviews(5, "train")
    validation = reviews(5, "validation")
    test = reviews(5, "test")
    validation.loc[0, "text"] = train.loc[0, "text"].upper()
    test.loc[0, "text"] = validation.loc[0, "text"]
    test.loc[1, "text"] = validation.loc[1, "text"]
    filtered_validation, filtered_test = filter_evaluation(train, validation, test)
    assert len(filtered_validation) == 24
    assert len(filtered_test) == 23


@pytest.mark.parametrize("change", ["missing", "null", "float", "range", "duplicate", "one_class"])
def test_input_validation(tmp_path, change):
    frame = reviews()
    if change == "missing":
        frame = frame.drop(columns="text")
    elif change == "null":
        frame.loc[0, "text"] = None
    elif change == "float":
        frame["label"] = frame["label"].astype(float)
    elif change == "range":
        frame.loc[0, "label"] = 7
    elif change == "duplicate":
        frame.loc[1, "id"] = frame.loc[0, "id"]
    else:
        frame = frame[frame["label"] == 0]
    frame.to_parquet(tmp_path / "reviews.parquet")
    with pytest.raises(ValueError):
        read_reviews(tmp_path / "reviews.parquet")


def test_real_search_metrics_saved_pipeline_and_no_vocabulary_leak(tmp_path):
    train, test = reviews(12, "train"), reviews(4, "testonlytoken")
    output = tmp_path / "run"
    result = compare_models(train, test, output, cv_folds=2, max_features=100)
    saved = json.loads((output / "resultados.json").read_text())
    assert saved["selected_model"] == max(saved["models"], key=lambda n: saved["models"][n]["cv_f1_macro"])
    assert set(result["models"]) == {"dummy", "logistic_regression", "random_forest", "linear_svm"}
    for metrics in result["models"].values():
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["f1_macro"] <= 1
        assert np.array(metrics["confusion_matrix"]).shape == (5, 5)
        assert np.array(metrics["confusion_matrix"]).sum() == len(test)
        assert set(metrics["per_class"]) == set(map(str, range(5)))
    pipeline = joblib.load(output / "best_model.joblib")
    assert "testonlytoken" not in pipeline.named_steps["tfidf"].vocabulary_
    assert len(pipeline.predict(test["text"])) == len(test)
    assert len(pd.read_csv(output / "particiones.csv")) == len(train) + len(test)
    assert len(list(output.glob("confusion_*.csv"))) == 4
    with pytest.raises(FileExistsError):
        compare_models(train, test, output)


def test_overlap_is_rejected_before_training(tmp_path):
    train, test = reviews(), reviews(prefix="test")
    test.loc[0, "text"] = train.loc[0, "text"].upper()
    with pytest.raises(ValueError, match="compartidos"):
        compare_models(train, test, tmp_path / "run")
    assert not (tmp_path / "run").exists()


def test_too_few_groups_rejected(tmp_path):
    with pytest.raises(ValueError):
        split_reviews(reviews(2))
    with pytest.raises(ValueError):
        compare_models(reviews(2), reviews(2, "test"), tmp_path / "run", cv_folds=3)


def test_cli_model_loads_from_another_process(tmp_path):
    train_path, test_path = tmp_path / "train.parquet", tmp_path / "test.parquet"
    reviews(6, "train").to_parquet(train_path)
    reviews(3, "test").to_parquet(test_path)
    output = tmp_path / "cli"
    subprocess.run([
        sys.executable, "-m", "src.modelos.comparar_ml", "--input", str(train_path),
        "--test-input", str(test_path), "--output", str(output), "--cv", "2",
        "--max-features", "100",
    ], check=True, capture_output=True, text=True)
    subprocess.run([
        sys.executable, "-c",
        "import joblib, sys; model = joblib.load(sys.argv[1]); "
        "assert len(model.predict(['Excelente servicio'])) == 1",
        str(output / "best_model.joblib"),
    ], check=True, capture_output=True, text=True)
