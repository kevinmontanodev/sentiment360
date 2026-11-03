import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.modelos import evaluar_umbrales
from src.modelos.evaluacion import (
    CostScenario, best_threshold, evaluate_threshold, evaluate_thresholds,
    is_unfavorable, unfavorable_probability,
)

# 6 reseñas de ejemplo: etiquetas reales y P(desfavorable) del modelo
LABELS = [0, 1, 1, 2, 3, 4]
P_UNFAVORABLE = np.array([0.87, 0.41, 0.35, 0.33, 0.10, 0.02])


def test_base_scenario_matches_documented_costs():
    scenario = CostScenario()
    assert scenario.cost_per_minute == pytest.approx(0.1179, abs=1e-4)
    assert scenario.fp_cost == pytest.approx(0.59, abs=0.01)
    assert scenario.tp_cost == pytest.approx(26.77, abs=0.01)
    assert scenario.fn_cost == pytest.approx(35.00)


def test_unfavorable_probability_uses_class_order():
    probabilities = np.array([[0.1, 0.2, 0.3, 0.2, 0.2]])
    assert unfavorable_probability(probabilities, [0, 1, 2, 3, 4]) == pytest.approx([0.3])
    assert unfavorable_probability(probabilities, [4, 3, 2, 1, 0]) == pytest.approx([0.4])


def test_three_stars_are_not_unfavorable():
    assert is_unfavorable(LABELS).tolist() == [True, True, True, False, False, False]


@pytest.mark.parametrize("threshold, expected", [
    (0.50, {"tp": 1, "fp": 0, "fn": 2, "tn": 3}),
    (0.30, {"tp": 3, "fp": 1, "fn": 0, "tn": 2}),
])
def test_evaluate_threshold_counts_outcomes(threshold, expected):
    result = evaluate_threshold(is_unfavorable(LABELS), P_UNFAVORABLE, threshold, CostScenario())
    assert {key: result[key] for key in expected} == expected


def test_net_benefit_formula():
    scenario = CostScenario()
    result = evaluate_threshold(is_unfavorable(LABELS), P_UNFAVORABLE, 0.30, scenario)
    saving = scenario.fn_cost - scenario.tp_cost
    assert result["net_benefit"] == pytest.approx(3 * saving - 1 * scenario.fp_cost)


def test_evaluate_thresholds_covers_0_01_to_0_99():
    results = evaluate_thresholds(is_unfavorable(LABELS), P_UNFAVORABLE, CostScenario())
    assert len(results) == 99
    assert results["threshold"].iloc[0] == 0.01
    assert results["threshold"].iloc[-1] == 0.99


def test_evaluate_thresholds_rejects_out_of_range():
    with pytest.raises(ValueError, match="0.01 y 0.99"):
        evaluate_thresholds(is_unfavorable(LABELS), P_UNFAVORABLE, CostScenario(), [0.0, 0.5])


def test_best_threshold_maximizes_net_benefit():
    results = evaluate_thresholds(is_unfavorable(LABELS), P_UNFAVORABLE, CostScenario())
    best = best_threshold(results)
    assert best["net_benefit"] == results["net_benefit"].max()
    # Entre 0.34 y 0.35 se marcan las tres reseñas desfavorables y ninguna de 3 estrellas
    assert best["threshold"] == 0.34


def _fake_split(seed):
    rng = np.random.default_rng(seed)
    words = {0: "horrible roto", 1: "malo tarde", 2: "regular normal", 3: "bueno util", 4: "excelente perfecto"}
    rows = [{"id": f"r{seed}-{i}", "text": f"{words[i % 5]} {rng.integers(1000)}", "label": i % 5} for i in range(100)]
    return pd.DataFrame(rows)


def test_main_writes_curve_results_and_plot(tmp_path):
    train = _fake_split(0)
    model = Pipeline([("tfidf", TfidfVectorizer()), ("clf", LogisticRegression(max_iter=1000))])
    model.fit(train["text"], train["label"])
    joblib.dump(model, tmp_path / "model.joblib")
    _fake_split(1).to_parquet(tmp_path / "validation.parquet", index=False)
    _fake_split(2).to_parquet(tmp_path / "test.parquet", index=False)
    output = tmp_path / "umbral"

    evaluar_umbrales.main([
        "--model", str(tmp_path / "model.joblib"), "--validation", str(tmp_path / "validation.parquet"),
        "--test", str(tmp_path / "test.parquet"), "--output", str(output),
    ])

    summary = json.loads((output / "resultados.json").read_text(encoding="utf-8"))
    assert len(pd.read_csv(output / "umbrales_validacion.csv")) == 99
    assert (output / "curva_beneficio_neto.png").exists()
    assert 0.01 <= summary["best_threshold_validation"] <= 0.99
    assert [row["customer_value"] for row in summary["sensitivity"]] == [50.0, 100.0, 200.0]
    assert set(summary["test"]) == {"chosen", "conventional", "gain_vs_conventional"}


def test_main_refuses_existing_output(tmp_path):
    (tmp_path / "out").mkdir()
    for name in ("m.joblib", "v.parquet", "t.parquet"):
        (tmp_path / name).write_text("x")
    with pytest.raises(SystemExit):
        evaluar_umbrales.main(["--model", str(tmp_path / "m.joblib"), "--validation", str(tmp_path / "v.parquet"),
                               "--test", str(tmp_path / "t.parquet"), "--output", str(tmp_path / "out")])