import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from src.modelos.evaluacion import (
    CostScenario, best_threshold, evaluate_threshold, evaluate_thresholds,
    is_unfavorable, plot_net_benefit, unfavorable_probability,
)

CONVENTIONAL_THRESHOLD = 0.5


def predict_unfavorable(model, frame: pd.DataFrame):
    """Devuelve las etiquetas binarias reales y P(desfavorable) del modelo"""
    probabilities = model.predict_proba(frame["text"])
    return is_unfavorable(frame["label"]), unfavorable_probability(probabilities, model.classes_)


def compare_on_test(y_test, p_test, threshold: float, scenario: CostScenario) -> dict:
    """Aplica en test el umbral elegido en validacion y el umbral convencional de 0.5"""
    chosen = evaluate_threshold(y_test, p_test, threshold, scenario)
    conventional = evaluate_threshold(y_test, p_test, CONVENTIONAL_THRESHOLD, scenario)
    return {
        "chosen": chosen,
        "conventional": conventional,
        "gain_vs_conventional": chosen["net_benefit"] - conventional["net_benefit"],
    }


def run(model, validation: pd.DataFrame, test: pd.DataFrame, customer_values: list[float]) -> tuple:
    y_val, p_val = predict_unfavorable(model, validation)
    y_test, p_test = predict_unfavorable(model, test)

    base = CostScenario()
    curve = evaluate_thresholds(y_val, p_val, base)
    best = best_threshold(curve)
    summary = {
        "decision_rule": "desfavorable = etiquetas 0 y 1 (1 y 2 estrellas)",
        "scenario": {**base.__dict__, "cost_per_minute": base.cost_per_minute,
                     "tp_cost": base.tp_cost, "fp_cost": base.fp_cost, "fn_cost": base.fn_cost},
        "validation_rows": len(validation),
        "test_rows": len(test),
        "unfavorable_share_test": float(y_test.mean()),
        "best_threshold_validation": float(best["threshold"]),
        "test": compare_on_test(y_test, p_test, float(best["threshold"]), base),
        "sensitivity": [],
    }
    for value in customer_values:
        scenario = CostScenario(customer_value=value)
        chosen = float(best_threshold(evaluate_thresholds(y_val, p_val, scenario))["threshold"])
        result = compare_on_test(y_test, p_test, chosen, scenario)
        summary["sensitivity"].append({
            "customer_value": value, "best_threshold": chosen,
            "net_benefit_test": result["chosen"]["net_benefit"],
            "net_benefit_test_at_0_5": result["conventional"]["net_benefit"],
        })
    return curve, summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evalua umbrales de decisión con una matriz de costos")
    parser.add_argument("--model", type=Path, default=Path("models/ml_20261102_final/best_model.joblib"))
    parser.add_argument("--validation", type=Path, default=Path("data/processed/ml_evaluacion/validation.parquet"))
    parser.add_argument("--test", type=Path, default=Path("data/processed/ml_evaluacion/test.parquet"))
    parser.add_argument("--output", type=Path, default=Path("reports/umbral"))
    parser.add_argument("--customer-values", type=float, nargs="+", default=[50.0, 100.0, 200.0])
    args = parser.parse_args(argv)

    for path in (args.model, args.validation, args.test):
        if not path.exists():
            parser.error(f"No existe {path}. Ejecuta primero la preparacion y el entrenamiento de la US-06")
    if args.output.exists():
        parser.error("La salida ya existe. Usa --output con otro directorio")

    model = joblib.load(args.model)
    validation = pd.read_parquet(args.validation)
    test = pd.read_parquet(args.test)
    curve, summary = run(model, validation, test, args.customer_values)

    args.output.mkdir(parents=True)
    curve.to_csv(args.output / "umbrales_validacion.csv", index=False)
    plot_net_benefit(curve, summary["best_threshold_validation"], args.output / "curva_beneficio_neto.png")
    (args.output / "resultados.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )

    chosen, conventional = summary["test"]["chosen"], summary["test"]["conventional"]
    print("Resumen de umbrales (US-08)")
    print(f"Umbral óptimo en validación: {summary['best_threshold_validation']:.2f}")
    print(f"Test con umbral óptimo: beneficio ${chosen['net_benefit']:,.2f} | "
          f"VP {chosen['tp']} FP {chosen['fp']} FN {chosen['fn']} | marcadas {chosen['flagged']}")
    print(f"Test con umbral 0.50:   beneficio ${conventional['net_benefit']:,.2f} | "
          f"VP {conventional['tp']} FP {conventional['fp']} FN {conventional['fn']} | marcadas {conventional['flagged']}")
    print(f"Diferencia: ${summary['test']['gain_vs_conventional']:,.2f}")
    print("Sensibilidad (valor del cliente → umbral, beneficio test):")
    for row in summary["sensitivity"]:
        print(f"  ${row['customer_value']:.0f} → {row['best_threshold']:.2f}, ${row['net_benefit_test']:,.2f} "
              f"(0.50: ${row['net_benefit_test_at_0_5']:,.2f})")
    print(f"Salida: {args.output}")


if __name__ == "__main__":
    main()