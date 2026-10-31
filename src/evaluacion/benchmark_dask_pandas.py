"""Benchmark de rendimiento entre Pandas y Dask."""

from __future__ import annotations

import json
import os
import platform
import statistics
import time
from pathlib import Path

import threading
import matplotlib.pyplot as plt
import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
import psutil


def get_system_info(dataset_path: Path) -> dict:
    """Obtiene información del equipo y del dataset."""

    return {
        "platform": platform.platform(),
        "processor": platform.processor() or "No disponible",
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "total_ram_gb": round(
            psutil.virtual_memory().total / (1024 ** 3), 2
        ),
        "available_ram_gb": round(
            psutil.virtual_memory().available / (1024 ** 3), 2
        ),
        "dataset_size_mb": round(
            sum(
                file.stat().st_size
                for file in dataset_path.rglob("*")
                if file.is_file()
            ) / (1024 ** 2),
            2,
        ),
    }


def pandas_aggregation(data: pd.DataFrame) -> pd.DataFrame:
    """Filtra reseñas y agrega métricas por sentimiento."""

    filtered = data[data["text"].notna() & (data["text"].str.len() > 0)]

    result = (
        filtered.assign(
            char_length=filtered["text"].str.len(),
            word_count=filtered["text"].str.split().str.len(),
        )
        .groupby("label")
        .agg(
            total_reviews=("id", "count"),
            avg_char_length=("char_length", "mean"),
            avg_word_count=("word_count", "mean"),
        )
        .sort_index()
    )

    return result


def dask_aggregation(data: dd.DataFrame) -> pd.DataFrame:
    """Ejecuta el mismo filtrado y agregación con Dask."""

    text_length = data["text"].str.len()

    filtered = data[
        (~data["text"].isna()) & (text_length > 0)
    ]

    filtered = filtered.assign(
        char_length=filtered["text"].str.len(),
        word_count=filtered["text"].str.split().str.len(),
    )

    result = (
        filtered.groupby("label")
        .agg(
            total_reviews=("id", "count"),
            avg_char_length=("char_length", "mean"),
            avg_word_count=("word_count", "mean"),
        )
        .compute(scheduler="threads")
        .sort_index()
    )

    return result



def measure_execution(function, data, repetitions: int) -> dict:
    """Mide tiempo y pico de memoria RAM por ejecución."""

    process = psutil.Process(os.getpid())

    times = []
    peak_memory_mb = []
    additional_memory_mb = []
    result = None

    for _ in range(repetitions):
        baseline_memory = process.memory_info().rss
        peak_memory = baseline_memory

        stop_monitor = threading.Event()

        def monitor_memory():
            nonlocal peak_memory

            while not stop_monitor.is_set():
                try:
                    current_memory = process.memory_info().rss
                    peak_memory = max(peak_memory, current_memory)
                except psutil.Error:
                    pass

                stop_monitor.wait(0.005)

        monitor = threading.Thread(
            target=monitor_memory,
            daemon=True,
        )

        monitor.start()
        start = time.perf_counter()

        try:
            result = function(data)
        finally:
            elapsed = time.perf_counter() - start
            stop_monitor.set()
            monitor.join()

            # Captura una última medición antes de finalizar.
            peak_memory = max(
                peak_memory,
                process.memory_info().rss,
            )

        times.append(elapsed)

        peak_mb = peak_memory / (1024 ** 2)
        baseline_mb = baseline_memory / (1024 ** 2)

        peak_memory_mb.append(peak_mb)
        additional_memory_mb.append(
            max(0, peak_mb - baseline_mb)
        )

    return {
        "times_seconds": [
            round(value, 6) for value in times
        ],
        "median_seconds": statistics.median(times),
        "peak_memory_mb": [
            round(value, 2) for value in peak_memory_mb
        ],
        "median_peak_memory_mb": round(
            statistics.median(peak_memory_mb), 2
        ),
        "additional_memory_mb": [
            round(value, 2) for value in additional_memory_mb
        ],
        "median_additional_memory_mb": round(
            statistics.median(additional_memory_mb), 2
        ),
        "result": result,
    }



def validate_equivalence(
    pandas_result: pd.DataFrame,
    dask_result: pd.DataFrame,
) -> bool:
    """Comprueba la equivalencia numérica de ambos resultados."""

    if not pandas_result.index.equals(dask_result.index):
        raise AssertionError("Las etiquetas no coinciden.")

    if not pandas_result["total_reviews"].equals(
        dask_result["total_reviews"]
    ):
        raise AssertionError("Los conteos no coinciden.")

    numeric_columns = [
        "avg_char_length",
        "avg_word_count",
    ]

    pandas_values = (
        pandas_result[numeric_columns]
        .astype("float64")
        .to_numpy()
    )

    dask_values = (
        dask_result[numeric_columns]
        .astype("float64")
        .to_numpy()
    )

    np.testing.assert_allclose(
        pandas_values,
        dask_values,
        rtol=1e-5,
        atol=0,
        equal_nan=True,
    )

    return True



def generate_benchmark_figures(
    report: dict,
    output_dir: str | Path = "reports/figures",
) -> None:
    """Genera gráficas comparativas del benchmark."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frameworks = ["Pandas", "Dask"]

    pandas_data = report["pandas"]
    dask_data = report["dask"]

    # 1. Comparación de tiempos medianos
    fig, ax = plt.subplots(figsize=(8, 5))

    times = [
        pandas_data["median_seconds"],
        dask_data["median_seconds"],
    ]

    bars = ax.bar(frameworks, times)

    ax.set_title("Comparación de rendimiento: Pandas vs Dask")
    ax.set_ylabel("Tiempo mediano (segundos)")
    ax.set_xlabel("Framework")
    ax.bar_label(bars, fmt="%.3f s", padding=4)

    fig.tight_layout()
    fig.savefig(
        output_dir / "benchmark_tiempos.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)

    # 2. Comparación de memoria
    fig, ax = plt.subplots(figsize=(9, 5))

    peak_memory = [
        pandas_data["median_peak_memory_mb"],
        dask_data["median_peak_memory_mb"],
    ]

    additional_memory = [
        pandas_data["median_additional_memory_mb"],
        dask_data["median_additional_memory_mb"],
    ]

    x = np.arange(len(frameworks))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        peak_memory,
        width,
        label="Pico RSS total",
    )

    bars2 = ax.bar(
        x + width / 2,
        additional_memory,
        width,
        label="Memoria adicional",
    )

    ax.set_title("Consumo de memoria: Pandas vs Dask")
    ax.set_ylabel("Memoria (MB)")
    ax.set_xticks(x)
    ax.set_xticklabels(frameworks)
    ax.legend()

    ax.bar_label(bars1, fmt="%.1f MB", padding=3)
    ax.bar_label(bars2, fmt="%.1f MB", padding=3)

    fig.tight_layout()
    fig.savefig(
        output_dir / "benchmark_memoria.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)

    # 3. Variabilidad entre ejecuciones
    fig, ax = plt.subplots(figsize=(8, 5))

    execution_data = [
        pandas_data["times_seconds"],
        dask_data["times_seconds"],
    ]

    positions = [1, 2]

    ax.boxplot(
        execution_data,
        tick_labels=frameworks,
        showmeans=True,
    )

    # Mostrar también cada ejecución individual.
    for position, executions in zip(positions, execution_data):
        ax.scatter(
            [position] * len(executions),
            executions,
            zorder=3,
        )

    ax.set_title("Variabilidad de los tiempos de ejecución")
    ax.set_ylabel("Tiempo (segundos)")
    ax.set_xlabel("Framework")

    fig.tight_layout()
    fig.savefig(
        output_dir / "benchmark_estabilidad.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)



def run_benchmark(
    dataset_path: str | Path,
    repetitions: int = 3,
    output_path: str | Path = "reports/benchmark/resultados.json",
) -> dict:
    """Ejecuta el benchmark Pandas vs Dask."""

    if repetitions < 3:
        raise ValueError("Se requieren al menos 3 ejecuciones.")

    dataset_path = Path(dataset_path)
    output_path = Path(output_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"No existe el dataset: {dataset_path}"
        )

    parquet_files = list(dataset_path.rglob("*.parquet"))

    if not parquet_files:
        raise ValueError("No se encontraron archivos Parquet.")

    # Se carga el mismo conjunto de datos para ambas tecnologías.
    pandas_data = pd.read_parquet(dataset_path)
    dask_data = dd.read_parquet(dataset_path)

    pandas_measurement = measure_execution(
        pandas_aggregation,
        pandas_data,
        repetitions,
    )

    dask_measurement = measure_execution(
        dask_aggregation,
        dask_data,
        repetitions,
    )

    equivalent = validate_equivalence(
        pandas_measurement["result"],
        dask_measurement["result"],
    )

    pandas_median = pandas_measurement["median_seconds"]
    dask_median = dask_measurement["median_seconds"]

    report = {
        "benchmark": "Pandas vs Dask",
        "repetitions": repetitions,
        "equivalent_results": equivalent,
        "pandas": {
            "times_seconds": pandas_measurement["times_seconds"],
            "median_seconds": round(pandas_median, 6),
            "peak_memory_mb": pandas_measurement["peak_memory_mb"],
            "median_peak_memory_mb": pandas_measurement[
                "median_peak_memory_mb"
            ],
            "additional_memory_mb": pandas_measurement[
                "additional_memory_mb"
            ],
            "median_additional_memory_mb": pandas_measurement[
                "median_additional_memory_mb"
            ],
        },
        "dask": {
            "times_seconds": dask_measurement["times_seconds"],
            "median_seconds": round(dask_median, 6),
            "peak_memory_mb": dask_measurement["peak_memory_mb"],
            "median_peak_memory_mb": dask_measurement[
                "median_peak_memory_mb"
            ],
            "additional_memory_mb": dask_measurement[
                "additional_memory_mb"
            ],
            "median_additional_memory_mb": dask_measurement[
                "median_additional_memory_mb"
            ],
        },
        "speedup": round(
            pandas_median / dask_median, 4
        ) if dask_median > 0 else None,
        "system": get_system_info(dataset_path),
        "results": {
            "pandas": pandas_measurement["result"].reset_index().to_dict(
                orient="records"
            ),
            "dask": dask_measurement["result"].reset_index().to_dict(
                orient="records"
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    generate_benchmark_figures(report)

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark de Pandas vs Dask."
    )
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument(
        "--output",
        default="reports/benchmark/resultados.json",
    )

    args = parser.parse_args()

    results = run_benchmark(
        dataset_path=args.dataset,
        repetitions=args.repetitions,
        output_path=args.output,
    )

    print(json.dumps(results, indent=4, ensure_ascii=False))
