"""Evaluacion de umbrales de decision mediante una matriz de costos"""

from dataclasses import dataclass
from collections.abc import Sequence
import numpy as np
import pandas as pd
from pathlib import Path

@dataclass(frozen=True)
class CostScenario:

    """Supuestos del escenario de simulacion (US Dollars)"""
    monthly_salary: float = 750.0
    employer_cost_rate: float = 0.259
    weekly_hours: float = 44.0
    shrinkage: float = 0.3
    review_minutes: float = 5.0
    contact_minutes: float = 10.0
    customer_value: float = 100.0
    churn_without_contact: float = 0.35
    churn_with_contact: float = 0.25

    @property
    def cost_per_minute(self) -> float:
        """Costo de un minuto productivo de un agente"""
        monthly_cost = self.monthly_salary * (1 + self.employer_cost_rate)
        monthly_hours = self.weekly_hours * 52 / 12
        productive_hours = monthly_hours * (1 - self.shrinkage)
        return monthly_cost / productive_hours / 60
    
    @property
    def fp_cost(self) -> float:
        """Falso positivo: el agente lee una reseña que no necesitaba atencion"""
        return self.review_minutes * self.cost_per_minute
    
    @property
    def tp_cost(self) -> float:
        """Verdadero positivo: el agente contacta al cliente y baja la probabilidad de abandono"""
        handling = (self.review_minutes + self.contact_minutes) * self.cost_per_minute
        return self.churn_with_contact * self.customer_value + handling
    
    @property
    def fn_cost(self) -> float:
        """Falso negativo: nadie contacta al cliente insatisfecho"""
        return self.churn_without_contact * self.customer_value
    

UNFAVORABLE_LABELS = (0, 1)


def unfavorable_probability(probabilities: np.ndarray, classes: Sequence[int]) -> np.ndarray:
    """Suma la probabilidad de 1 y 2 estrellas (etiquetas 0 y 1)"""
    columns = [list(classes).index(label) for label in UNFAVORABLE_LABELS]
    return np.asarray(probabilities)[:, columns].sum(axis=1)


def is_unfavorable(labels: Sequence[int]) -> np.ndarray:
    """Convierte las 5 etiquetas en la decision del negocio: desfavorable o no"""
    return np.isin(np.asarray(labels), UNFAVORABLE_LABELS)


def evaluate_threshold(
        y_true: np.ndarray, p_unfavorable: np.ndarray, threshold: float, scenario: CostScenario
) -> dict:
    """Cuenta VP, FP, FN y VN para un umbral y calcula el beneficio simulado"""
    flagged = p_unfavorable >= threshold
    tp = int(np.sum(flagged & y_true))
    fp = int(np.sum(flagged & ~y_true))
    fn = int(np.sum(~flagged & y_true))
    tn = int(np.sum(~flagged & ~y_true))
    total_cost = tp * scenario.tp_cost + fp * scenario.fp_cost + fn * scenario.fn_cost
    # Beneficio frente a no revisar ninguna reseña: cada VP evita un FN y cada FP cuesta tiempo
    net_benefit = tp * (scenario.fn_cost - scenario.tp_cost) - fp * scenario.fp_cost
    return {
        "threshold": round(float(threshold), 2), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "flagged": tp + fp, "recall": tp / (tp + fn) if tp + fn else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "total_cost": total_cost, "net_benefit": net_benefit,
    }


def evaluate_thresholds(
    y_true: Sequence[bool],
    p_unfavorable: Sequence[float],
    scenario: CostScenario,
    thresholds: Sequence[float] | None = None,
) -> pd.DataFrame:
    """Evalua los umbrales de 0.01 a 0.99 (o los indicados) y devuelve una fila por umbral"""
    y_true = np.asarray(y_true, dtype=bool)
    p_unfavorable = np.asarray(p_unfavorable, dtype=float)
    if thresholds is None:
        thresholds = np.round(np.arange(0.01, 1.0, 0.01), 2)
    thresholds = np.asarray(thresholds, dtype=float)
    if thresholds.size == 0 or thresholds.min() < 0.01 or thresholds.max() > 0.99:
        raise ValueError("Los umbrales deben estar entre 0.01 y 0.99")
    if len(y_true) != len(p_unfavorable):
        raise ValueError("Las etiquetas y las probabilidades deben tener el mismo tamaño")
    rows = [evaluate_threshold(y_true, p_unfavorable, t, scenario) for t in thresholds]
    return pd.DataFrame(rows)


def best_threshold(results: pd.DataFrame) -> pd.Series:
    """Fila con el mayor beneficio neto; ante un empate se elige el umbral mas bajo"""
    return results.loc[results["net_benefit"].idxmax()]


def plot_net_benefit(results: pd.DataFrame, best: float, output_path: Path) -> None:
    """Dibuja la curva de beneficio neto y marca el umbral optimo y el de 0.5"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(results["threshold"], results["net_benefit"], color="#1f77b4", linewidth=2)
    ax.axvline(best, color="#2ca02c", linestyle="--", label=f"Optimo ({best:.2f})")
    ax.axvline(0.5, color="#7f7f7f", linestyle=":", label="Convencional (0.50)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Umbral de decision para P(desfavorable)")
    ax.set_ylabel("Beneficio neto simulado (USD)")
    ax.set_title("Beneficio neto segun el umbral (validacion)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)