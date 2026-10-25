"""Ejecutar desde la raíz: python -m src.procesamiento.procesar_pyspark."""

import argparse
import json
import math
from pathlib import Path

import dask
import dask.dataframe as dd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.procesamiento.limpiar_resenas import DTYPES


def create_spark_session(app_name: str = "Sentiment360-US04") -> SparkSession:
    """Crea o reutiliza una sesión de Spark configurada en modo local."""
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )


def _resolve_parquet_files(parquet_dir: str | Path) -> Path:
    """Verifica que el directorio exista y contenga archivos Parquet."""
    path = Path(parquet_dir)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"El directorio Parquet no existe: {path}")
    if not list(path.glob("*.parquet")):
        raise FileNotFoundError(f"No se encontraron archivos .parquet en: {path}")
    return path


def process_with_pyspark(
    parquet_dir: str | Path,
    spark: SparkSession | None = None,
) -> dict:
    """
    Lee el Parquet de la US-03 y calcula métricas por etiqueta usando PySpark.

    Separa explícitamente las transformaciones perezosas (construcción del DAG)
    de las acciones (que disparan la ejecución en el motor de Spark).
    """
    path = _resolve_parquet_files(parquet_dir)
    own_session = spark is None
    session = spark or create_spark_session()

    try:
        # 1. Transformación perezosa: lectura del conjunto de datos Parquet
        df = session.read.parquet(str(path))
        if list(df.columns) != list(DTYPES):
            raise ValueError("El Parquet no contiene las columnas esperadas.")

        # 2. Transformaciones perezosas: columnas derivadas y agregación por etiqueta
        df_transformed = df.withColumns(
            {
                "char_length": F.length(F.col("text")),
                "word_count": F.size(F.split(F.col("text"), " ")),
            }
        )

        df_aggregated = (
            df_transformed.groupBy("label")
            .agg(
                F.count("id").alias("count"),
                F.round(F.avg("char_length"), 2).alias("avg_char_length"),
                F.round(F.avg("word_count"), 2).alias("avg_word_count"),
            )
            .orderBy("label")
        )

        # 3. Acciones: fuerzan la evaluación del plan lógico y físico en Spark
        total_reviews = df.count()
        rows = df_aggregated.collect()

        labels_count = {str(label): 0 for label in range(5)}
        metrics_by_label = {}

        for row in rows:
            label_key = str(row["label"])
            count_val = int(row["count"])
            labels_count[label_key] = count_val
            metrics_by_label[label_key] = {
                "count": count_val,
                "avg_char_length": float(row["avg_char_length"]),
                "avg_word_count": float(row["avg_word_count"]),
            }

        return {
            "engine": "pyspark",
            "total_reviews": int(total_reviews),
            "labels": labels_count,
            "metrics_by_label": metrics_by_label,
        }
    finally:
        if own_session:
            session.stop()


def process_with_dask(parquet_dir: str | Path) -> dict:
    """Realiza la operación equivalente con Dask sobre el mismo conjunto de datos."""
    path = _resolve_parquet_files(parquet_dir)

    # 1. Construcción diferida del grafo de tareas en Dask
    frame = dd.read_parquet(str(path / "*.parquet"), engine="pyarrow")
    if list(frame.columns) != list(DTYPES):
        raise ValueError("El Parquet no contiene las columnas esperadas.")

    frame = frame.assign(
        char_length=frame["text"].str.len(),
        word_count=frame["text"].str.split(" ").str.len(),
    )

    grouped = frame.groupby("label").agg(
        count=("id", "count"),
        avg_char_length=("char_length", "mean"),
        avg_word_count=("word_count", "mean"),
    )

    # 2. Acción en Dask: dask.compute() materializa el grafo en memoria
    total_reviews, grouped_df = dask.compute(
        frame.shape[0],
        grouped,
        scheduler="threads",
    )

    labels_count = {str(label): 0 for label in range(5)}
    metrics_by_label = {}

    grouped_df = grouped_df.sort_index()
    for label, row in grouped_df.iterrows():
        count_val = int(row["count"])
        if count_val > 0:
            label_key = str(int(label))
            labels_count[label_key] = count_val
            metrics_by_label[label_key] = {
                "count": count_val,
                "avg_char_length": round(float(row["avg_char_length"]), 2),
                "avg_word_count": round(float(row["avg_word_count"]), 2),
            }

    return {
        "engine": "dask",
        "total_reviews": int(total_reviews),
        "labels": labels_count,
        "metrics_by_label": metrics_by_label,
    }


def compare_spark_and_dask(
    parquet_dir: str | Path,
    spark: SparkSession | None = None,
) -> dict:
    """Ejecuta el procesamiento en PySpark y Dask y comprueba su consistencia."""
    spark_result = process_with_pyspark(parquet_dir, spark=spark)
    dask_result = process_with_dask(parquet_dir)

    if spark_result["total_reviews"] != dask_result["total_reviews"]:
        raise ValueError(
            "Inconsistencia en el total de reseñas entre PySpark y Dask."
        )

    if spark_result["labels"] != dask_result["labels"]:
        raise ValueError(
            "Inconsistencia en el conteo por etiqueta entre PySpark y Dask."
        )

    for label, spark_metric in spark_result["metrics_by_label"].items():
        dask_metric = dask_result["metrics_by_label"].get(label)
        if dask_metric is None:
            raise ValueError(f"Falta la etiqueta {label} en los resultados de Dask.")
        if not math.isclose(
            spark_metric["avg_char_length"],
            dask_metric["avg_char_length"],
            abs_tol=0.05,
        ) or not math.isclose(
            spark_metric["avg_word_count"],
            dask_metric["avg_word_count"],
            abs_tol=0.05,
        ):
            raise ValueError(
                f"Inconsistencia en promedios para la etiqueta {label}."
            )

    return {
        "consistent": True,
        "total_reviews": spark_result["total_reviews"],
        "labels": spark_result["labels"],
        "pyspark": spark_result["metrics_by_label"],
        "dask": dask_result["metrics_by_label"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procesa reseñas en Parquet con PySpark y compara resultados con Dask."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/reviews"),
        help="Directorio Parquet generado por la US-03.",
    )
    args = parser.parse_args()

    summary = compare_spark_and_dask(args.input)
    print("Resumen comparativo PySpark vs Dask")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()