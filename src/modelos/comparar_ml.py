"""Comparación reproducible de modelos clásicos sobre reseñas Parquet."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.modelos.texto import normalize_text

LABELS = list(range(5))


def read_reviews(path: str | Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    if not {"id", "text", "label"}.issubset(frame.columns):
        raise ValueError("El Parquet debe contener id, text y label.")
    frame = frame[["id", "text", "label"]].copy()
    for column in ("id", "text"):
        if not frame[column].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
            raise ValueError(f"La columna {column} contiene valores inválidos.")
    if not pd.api.types.is_integer_dtype(frame["label"]) or not frame["label"].isin(LABELS).all():
        raise ValueError("Las etiquetas deben ser enteros de 0 a 4.")
    if set(frame["label"]) != set(LABELS):
        raise ValueError("Se necesitan las cinco etiquetas; no uses las primeras filas del corpus.")
    if frame["id"].duplicated().any():
        raise ValueError("Los identificadores deben ser únicos.")
    return frame.reset_index(drop=True)


def split_reviews(frame: pd.DataFrame, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reserva aproximadamente 20 % sin compartir textos normalizados."""
    groups = frame["text"].map(normalize_text)
    if groups.groupby(frame["label"]).nunique().min() < 5:
        raise ValueError("Se necesitan al menos cinco textos distintos por etiqueta.")
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_index, test_index = next(splitter.split(frame["text"], frame["label"], groups))
    return frame.iloc[train_index].reset_index(drop=True), frame.iloc[test_index].reset_index(drop=True)


def dataset_fingerprint(frame: pd.DataFrame) -> str:
    rows = frame.sort_values("id").to_json(orient="records", force_ascii=False)
    return hashlib.sha256(rows.encode("utf-8")).hexdigest()


def model_candidates(seed: int) -> dict:
    return {
        "dummy": (DummyClassifier(strategy="most_frequent"), {}),
        "logistic_regression": (
            LogisticRegression(max_iter=1000, random_state=seed), {"classifier__C": [0.5, 2.0]},
        ),
        "random_forest": (
            RandomForestClassifier(n_estimators=80, random_state=seed, n_jobs=1),
            {"classifier__max_depth": [30, None]},
        ),
        "linear_svm": (LinearSVC(random_state=seed, max_iter=5000), {"classifier__C": [0.5, 2.0]}),
    }


def compare_models(
    train: pd.DataFrame,
    test: pd.DataFrame,
    output_dir: str | Path,
    seed: int = 42,
    cv_folds: int = 3,
    max_train: int | None = None,
    max_features: int = 20000,
) -> dict:
    """Selecciona por F1 macro de CV; consulta prueba después de elegir."""
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError("La salida ya existe; elige otro directorio.")
    if cv_folds < 2 or max_features <= 0:
        raise ValueError("CV debe tener al menos dos folds y max_features debe ser positivo.")
    if max_train is not None and max_train < 5 * cv_folds:
        raise ValueError("max_train no permite representar las cinco clases en CV.")
    for frame in (train, test):
        if set(frame["label"]) != set(LABELS):
            raise ValueError("Entrenamiento y prueba deben contener las cinco clases.")
    train_keys = train["text"].map(normalize_text)
    test_keys = test["text"].map(normalize_text)
    if set(train["id"]) & set(test["id"]) or set(train_keys) & set(test_keys):
        raise ValueError("Hay IDs o textos compartidos entre entrenamiento y prueba.")

    available_train = len(train)
    if max_train is not None and max_train < len(train):
        train, _ = train_test_split(
            train, train_size=max_train, stratify=train["label"], random_state=seed,
        )
    train = train.reset_index(drop=True)
    groups = train["text"].map(normalize_text)
    if groups.groupby(train["label"]).nunique().min() < cv_folds:
        raise ValueError("No hay suficientes grupos por etiqueta para CV.")
    splitter = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    folds = list(splitter.split(train["text"], train["label"], groups))
    for fit_index, validation_index in folds:
        if any(set(train.iloc[index]["label"]) != set(LABELS) for index in (fit_index, validation_index)):
            raise ValueError("Un fold no contiene las cinco clases; aumenta los datos o reduce CV.")

    report = {
        "seed": seed, "cv_folds": cv_folds, "selection_metric": "cv_f1_macro",
        "available_train": available_train, "train_rows": len(train), "test_rows": len(test),
        "max_features": max_features, "exact_text_overlap": 0,
        "train_sha256": dataset_fingerprint(train), "test_sha256": dataset_fingerprint(test),
        "train_label_counts": train["label"].value_counts().sort_index().to_dict(),
        "test_label_counts": test["label"].value_counts().sort_index().to_dict(),
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                        "pandas": pd.__version__, "numpy": np.__version__, "platform": platform.platform()},
        "models": {},
    }
    fitted = {}
    for name, (classifier, parameters) in model_candidates(seed).items():
        print(f"Entrenando {name} con {len(train)} reseñas y {cv_folds} folds...", flush=True)
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(preprocessor=normalize_text, ngram_range=(1, 2),
                                      min_df=2, max_features=max_features, sublinear_tf=True)),
            ("classifier", classifier),
        ])
        search = GridSearchCV(pipeline, parameters, cv=folds, scoring="f1_macro",
                              refit=True, n_jobs=1, error_score="raise")
        started = perf_counter()
        search.fit(train["text"], train["label"])
        report["models"][name] = {
            "cv_f1_macro": float(search.best_score_),
            "cv_std": float(search.cv_results_["std_test_score"][search.best_index_]),
            "best_params": search.best_params_, "fit_seconds": perf_counter() - started,
            "search_results": [
                {"params": params, "mean_f1_macro": float(mean), "std_f1_macro": float(std)}
                for params, mean, std in zip(search.cv_results_["params"],
                    search.cv_results_["mean_test_score"], search.cv_results_["std_test_score"])
            ],
        }
        fitted[name] = search.best_estimator_

    # El conjunto de prueba no participa en la selección ni en los hiperparámetros.
    winner = max(report["models"], key=lambda name: report["models"][name]["cv_f1_macro"])
    report["selected_model"] = winner
    for name, pipeline in fitted.items():
        predicted = pipeline.predict(test["text"])
        metrics = classification_report(test["label"], predicted, labels=LABELS,
                                        output_dict=True, zero_division=0)
        report["models"][name].update({
            "accuracy": accuracy_score(test["label"], predicted),
            "precision_macro": metrics["macro avg"]["precision"],
            "recall_macro": metrics["macro avg"]["recall"],
            "f1_macro": metrics["macro avg"]["f1-score"],
            "f1_weighted": metrics["weighted avg"]["f1-score"],
            "per_class": {str(label): metrics[str(label)] for label in LABELS},
            "confusion_matrix": confusion_matrix(test["label"], predicted, labels=LABELS).tolist(),
        })

    output.mkdir(parents=True)
    joblib.dump(fitted[winner], output / "best_model.joblib")
    (output / "resultados.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    # Se guardan IDs, particiones y hashes, sin redistribuir los textos.
    partitions = pd.concat([train[["id", "label"]].assign(partition="train"),
                            test[["id", "label"]].assign(partition="test")])
    partitions.to_csv(output / "particiones.csv", index=False)
    for name, metrics in report["models"].items():
        pd.DataFrame(metrics["confusion_matrix"], index=LABELS, columns=LABELS).to_csv(
            output / f"confusion_{name}.csv", index_label="real/predicha",
        )
    print(f"Mejor modelo por CV: {winner}", flush=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara Dummy, Regresión Logística, RF y SVM.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/reviews"))
    parser.add_argument("--test-input", type=Path, help="Prueba externa sin textos compartidos.")
    parser.add_argument("--output", type=Path, default=Path("models/ml"))
    parser.add_argument("--max-train", type=int, default=None)
    parser.add_argument("--cv", type=int, default=3)
    parser.add_argument("--max-features", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    train = read_reviews(args.input)
    if args.test_input:
        test = read_reviews(args.test_input)
    else:
        train, test = split_reviews(train, args.seed)
    compare_models(train, test, args.output, args.seed, args.cv, args.max_train, args.max_features)


if __name__ == "__main__":
    main()
