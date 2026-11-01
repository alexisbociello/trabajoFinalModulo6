"""Ampliación MLOps: entrenar M1 y comparar contra M0 sin mezclar tiempos."""
from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .comun import (VERSION, SCHEMAS, ContractError, baseline, load_validated,
                    require, sha256, timestamp, write_csv, write_json)

PERIODS = {
    "entrenamiento": (date(2025, 1, 1), date(2025, 3, 31)),
    "validacion": (date(2025, 4, 1), date(2025, 4, 30)),
    "prueba": (date(2025, 5, 1), date(2025, 5, 31)),
}


def examples(data):
    """Objetivo: suma próximos siete días; x: suma siete días hasta el origen."""
    result = []
    groups = sorted((b["sucursal_id"], p["producto_id"]) for b in data["branches"] for p in data["products"])
    for branch, product in groups:
        origin = date(2025, 1, 7)
        while origin <= date(2025, 5, 24):
            target_start, target_end = origin + timedelta(days=1), origin + timedelta(days=7)
            partition = next((name for name, (start, end) in PERIODS.items()
                              if start <= target_start and target_end <= end), None)
            if partition:
                x = baseline(data, origin, branch, product)
                y = 0
                for offset in range(1, 8):
                    key = (origin + timedelta(days=offset), branch, product)
                    require(key in data["daily"] and key in data["inventory"], f"Falta objetivo completo para origen {origin}")
                    inventory = data["inventory"][key]
                    require(inventory["ventas_completas"] and not inventory["quiebre"], f"Objetivo censurado/incompleto: {key}")
                    label_cutoff = datetime.combine(PERIODS[partition][1], datetime.max.time(), tzinfo=timezone.utc)
                    require(data["daily"][key]["max_ingesta"] <= label_cutoff and inventory["ingesta"] <= label_cutoff,
                            "Etiqueta disponible después del fin de su partición")
                    y += data["daily"][key]["unidades"]
                result.append({"sucursal_id": branch, "producto_id": product, "origen": origin.isoformat(),
                               "fin_caracteristicas": origin.isoformat(), "objetivo_desde": target_start.isoformat(),
                               "objetivo_hasta": target_end.isoformat(), "particion": partition, "x_ultimos7": x, "y_proximos7": y})
            origin += timedelta(days=1)
    return result


def fit(rows):
    require(len(rows) >= 2, "M1 requiere al menos dos ejemplos de entrenamiento")
    xbar = sum(r["x_ultimos7"] for r in rows) / len(rows)
    ybar = sum(r["y_proximos7"] for r in rows) / len(rows)
    denominator = sum((r["x_ultimos7"] - xbar) ** 2 for r in rows)
    slope = (sum((r["x_ultimos7"] - xbar) * (r["y_proximos7"] - ybar) for r in rows) / denominator) if denominator else 0.0
    return {"intercepto": ybar - slope * xbar, "pendiente": slope, "n_entrenamiento": len(rows),
            "x_constante": denominator == 0}


def predict(model, x):
    return max(0.0, model["intercepto"] + model["pendiente"] * x)


def metric(rows, model_key):
    require(rows, "No hay observaciones para evaluar")
    error = sum(abs(r["real"] - r[model_key]) for r in rows)
    total = sum(abs(r["real"]) for r in rows)
    return {"n": len(rows), "MAE_unidades": round(error / len(rows), 8),
            "WAPE_porcentaje": round(100 * error / total, 8) if total else None,
            "suma_reales": total, "suma_errores_absolutos": round(error, 8)}


def train(data_dir, output_dir):
    root, out = Path(data_dir), Path(output_dir)
    require(not out.exists(), "La carpeta de salida ya existe; use otro nombre")
    out.mkdir(parents=True)
    manifest = {"estado": "INICIADA", "version_codigo": VERSION,
                "inicio_utc": datetime.now(timezone.utc).isoformat(),
                "entorno": {"python": platform.python_version(), "sistema": platform.platform()},
                "archivos_entrada_sha256": {name: sha256(root / name) for name in SCHEMAS if (root / name).exists()},
                "codigo_sha256": {p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))}}
    try:
        data = load_validated(root, timestamp("2025-06-30T23:59:59Z"))
        rows = examples(data)
        models = {}
        for product in sorted({r["producto_id"] for r in rows}):
            selected = [r for r in rows if r["particion"] == "entrenamiento" and r["producto_id"] == product]
            models[product] = fit(selected)
        artifact = {"id": "M1", "version": "M1-lineal-1.0", "estado": "CANDIDATO_NO_APROBADO",
                    "algoritmo": "Mínimos cuadrados: y_7d = intercepto + pendiente * suma_ultimos7; piso 0 en inferencia",
                    "feature_version": "suma_7d-1.0", "horizonte_dias": 7,
                    "ajustado_con_objetivos_hasta": "2025-03-31", "modelos_por_producto": models,
                    "hiperparametros": "Sin búsqueda ni ajuste con validación/prueba; especificación fijada antes de observar métricas",
                    "limite": "Datos artificiales; no prueba desempeño real ni demanda censurada"}
        predictions = []
        for row in rows:
            if row["particion"] == "entrenamiento":
                continue
            pred = predict(models[row["producto_id"]], row["x_ultimos7"])
            predictions.append({"particion": row["particion"], "origen": row["origen"], "objetivo_desde": row["objetivo_desde"],
                                "objetivo_hasta": row["objetivo_hasta"], "sucursal_id": row["sucursal_id"], "producto_id": row["producto_id"],
                                "real": row["y_proximos7"], "M0": row["x_ultimos7"], "M1": round(pred, 8)})
        metrics = {"origen": "Calculadas por esta ejecución sobre CSV sintéticos; no son las cuatro filas ilustrativas del libro",
                   "evaluacion": {}, "seleccion": "M0 se mantiene aprobado; revisión humana de M1 sin promoción automática"}
        for part in ("validacion", "prueba"):
            selected = [r for r in predictions if r["particion"] == part]
            metrics["evaluacion"][part] = {"global": {m: metric(selected, m) for m in ("M0", "M1")},
                "por_producto": {p: {m: metric([r for r in selected if r["producto_id"] == p], m) for m in ("M0", "M1")}
                                 for p in sorted(models)}}
        write_json(out / "modelo_m1.json", artifact)
        write_json(out / "metricas.json", metrics)
        write_csv(out / "particiones.csv", rows, list(rows[0]))
        write_csv(out / "predicciones_evaluacion.csv", predictions, list(predictions[0]))
        text = ["# Decisión del modelo", "", "M0 permanece aprobado. M1 queda como candidato para revisión humana.", "",
                "M1 se ajustó con objetivos completos hasta el 31 de marzo. Validación: abril. Prueba final: mayo.",
                "Las ventanas objetivo que cruzan meses de partición se excluyeron. Las variables usan únicamente los siete días hasta el origen.",
                "No se ajustaron parámetros después de observar validación o prueba. Repetir decisiones hasta mejorar la prueba dejaría de ser evaluación final.",
                "Los ejemplos se solapan dentro de cada partición: las métricas son descriptivas y no una prueba de significación estadística.",
                "El caso representa demanda libre sintética sin quiebres. No demuestra predicción comercial ni identificación de demanda no satisfecha.", "",
                "|Periodo|MAE M0|MAE M1|WAPE M0 (%)|WAPE M1 (%)|", "|---|---:|---:|---:|---:|"]
        for part in ("validacion", "prueba"):
            m = metrics["evaluacion"][part]["global"]
            text.append(f"|{part}|{m['M0']['MAE_unidades']}|{m['M1']['MAE_unidades']}|{m['M0']['WAPE_porcentaje']}|{m['M1']['WAPE_porcentaje']}|")
        text.extend(["", "Revisar métricas por producto, estabilidad, costo y limitaciones antes de promover. El pipeline de reposición solo admite M0.",
                     "Una promoción futura requiere otra versión de configuración e integración de inferencia, pruebas y aprobación humana."])
        (out / "decision_modelo.md").write_text("\n".join(text) + "\n", encoding="utf-8")
        manifest["estado"] = "COMPLETADA_CANDIDATO_NO_APROBADO"
        manifest["archivos_salida_sha256"] = {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()}
        return metrics
    except (ContractError, OSError, ValueError, KeyError) as exc:
        manifest["estado"] = "BLOQUEADA"
        manifest["error"] = str(exc)
        raise ContractError(str(exc)) from exc
    finally:
        manifest["fin_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(out / "manifiesto.json", manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", default="datos")
    parser.add_argument("--salida", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(train(args.datos, args.salida), ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError) as exc:
        print("BLOQUEADO: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
