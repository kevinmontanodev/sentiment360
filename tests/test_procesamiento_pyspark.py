"""Pruebas unitarias para el procesamiento con PySpark y comparación con Dask (US-04)."""

from pathlib import Path
import pytest

from src.procesamiento.limpiar_resenas import process_reviews
from src.procesamiento.procesar_pyspark import (
    compare_spark_and_dask,
    create_spark_session,
    process_with_dask,
    process_with_pyspark,
)


@pytest.fixture(scope="module")
def spark_session():
    """Sesión de Spark compartida para las pruebas del módulo."""
    session = create_spark_session("Sentiment360-US04-Tests")
    yield session
    session.stop()


def _sample_reviews() -> list[dict]:
    return [
        {
            "id": "es_001",
            "text": "Excelente producto muy buena calidad",
            "label": 4,
            "label_text": "4",
        },
        {
            "id": "es_002",
            "text": "Buen servicio y entrega rápida",
            "label": 4,
            "label_text": "4",
        },
        {
            "id": "es_003",
            "text": "Llegó roto y tarde",
            "label": 0,
            "label_text": "0",
        },
        {
            "id": "es_004",
            "text": "Calidad regular por el precio",
            "label": 2,
            "label_text": "2",
        },
    ]


def test_pyspark_and_dask_consistency(tmp_path: Path, spark_session) -> None:
    """Verifica que PySpark y Dask produzcan conteos y agregaciones consistentes."""
    parquet_dir = tmp_path / "reviews"
    process_reviews(_sample_reviews(), parquet_dir, batch_size=2)

    comparison = compare_spark_and_dask(parquet_dir, spark=spark_session)

    assert comparison["consistent"] is True
    assert comparison["total_reviews"] == 4
    assert comparison["labels"] == {"0": 1, "1": 0, "2": 1, "3": 0, "4": 2}
    assert comparison["pyspark"]["4"]["count"] == 2
    assert comparison["dask"]["4"]["count"] == 2
    assert (
        comparison["pyspark"]["0"]["avg_word_count"]
        == comparison["dask"]["0"]["avg_word_count"]
    )


def test_empty_parquet_consistency(tmp_path: Path, spark_session) -> None:
    """Evalúa cómo reaccionan PySpark y Dask ante un Parquet válido sin registros."""
    parquet_dir = tmp_path / "empty_reviews"
    process_reviews([], parquet_dir, batch_size=10)

    spark_res = process_with_pyspark(parquet_dir, spark=spark_session)
    dask_res = process_with_dask(parquet_dir)

    assert spark_res["total_reviews"] == 0
    assert dask_res["total_reviews"] == 0
    assert spark_res["labels"] == dask_res["labels"]


def test_missing_directory_raises_error(tmp_path: Path, spark_session) -> None:
    """Comprueba que una ruta inexistente lance FileNotFoundError."""
    missing_dir = tmp_path / "no_existe"
    with pytest.raises(FileNotFoundError):
        process_with_pyspark(missing_dir, spark=spark_session)