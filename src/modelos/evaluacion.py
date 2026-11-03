"""Evaluacion de umbrales de decision mediante una matriz de costos"""

from dataclasses import dataclass
from collections.abc import Sequence
import numpy as np
import pandas as pd

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
    """Evalúa los umbrales de 0.01 a 0.99 (o los indicados) y devuelve una fila por umbral"""
    y_true = np.asarray(y_true, dtype=bool)
    p_unfavorable = np.asarray(p_unfavorable, dtype=float)
    if thresholds is None:
        thresholds = np.round(np.arange(0.01, 1.0, 0.01), 2)
    thresholds = np.asarray(thresholds, dtype=float)
    if thresholds.size == 0 or thresholds.min() < 0.01 or thresholds.max() > 0.99:
        raise ValueError("Los umbrales deben estar entre 0.01 y 0.99")
    if len(y_true) != len(p_unfavorable):
        raise ValueError("Las etiquetas y las probabilidades deben tener el mismo tamaño.")
    rows = [evaluate_threshold(y_true, p_unfavorable, t, scenario) for t in thresholds]
    return pd.DataFrame(rows)


def best_threshold(results: pd.DataFrame) -> pd.Series:
    """Fila con el mayor beneficio neto; ante un empate se elige el umbral más bajo"""
    return results.loc[results["net_benefit"].idxmax()]
