"""Ejecutar: python -m src.pipeline --config config/ejecucion.json --salida salidas/local_v1"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from .comun import (VERSION, SCHEMAS, ContractError, baseline, day, integer,
                    load_validated, money, replenish, require, sha256,
                    timestamp, write_csv, write_json)


def run(data_dir, config_file, output_dir):
    root, config_file, out = Path(data_dir), Path(config_file), Path(output_dir)
    require(not out.exists(), "La carpeta de salida ya existe; use otro nombre de corrida")
    out.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    manifest = {"version_codigo": VERSION, "inicio_utc": started, "estado": "INICIADA",
                "entorno": {"python": platform.python_version(), "sistema": platform.platform()},
                "archivos_entrada_sha256": {}, "archivos_salida_sha256": {},
                "codigo_sha256": {p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))}}
    try:
        for name in list(SCHEMAS) + ["snapshot_fuentes.json"]:
            if (root / name).is_file():
                manifest["archivos_entrada_sha256"][name] = sha256(root / name)
        config = json.loads(config_file.read_text(encoding="utf-8"))
        manifest["configuracion"] = config
        manifest["config_sha256"] = sha256(config_file)
        cutoff = timestamp(config["corte"])
        decision = day(config["fecha_decision"])
        require(decision == cutoff.date(), "Esta práctica utiliza decisión en la fecha del corte")
        require(config["modelo_aprobado"] == "M0", "Solo M0 está aprobado en esta práctica; M1 es un candidato separado")
        require(config["reservas_fuera_del_pronostico"] is True,
                "No se ha conciliado el universo de reservas con el pronóstico")
        require(config["modo"] in {"operativo_didactico", "contrafactual"}, "Modo de corrida desconocido")
        policy_path = config_file.parent / config["politica_archivo"]
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        manifest["politica"] = policy
        manifest["politica_sha256"] = sha256(policy_path)
        horizon = integer(policy["horizonte_dias"], "horizonte_dias", 1)
        require(horizon == 7, "El baseline implementado tiene horizonte de 7 días")
        safety = integer(policy["dias_seguridad"], "dias_seguridad")
        valid_policy = day(policy["desde"]) <= decision and (not policy["hasta"] or decision < day(policy["hasta"]))
        require(valid_policy or config["modo"] == "contrafactual", "Política no vigente para la fecha de decisión")
        data = load_validated(root, cutoff)
        quality = data["quality"]
        manifest["version_datos"] = data["snapshot"].get("data_version", "no_declarada")
        quality["pedidos_excluidos_transito"] = []
        if not valid_policy:
            quality["advertencias"].append("Política fuera de vigencia aplicada únicamente como escenario contrafactual")
        daily_rows = []
        for (when, branch, product), item in sorted(data["daily"].items()):
            daily_rows.append({"fecha": when.isoformat(), "sucursal_id": branch, "producto_id": product,
                               "lineas": item["lineas"], "unidades": item["unidades"], "ventas_netas": money(item["ventas_netas"]),
                               "costos": money(item["costos"]), "margen": money(item["ventas_netas"] - item["costos"])})
        forecast_rows, replenish_rows = [], []
        groups = sorted((b["sucursal_id"], p["producto_id"]) for b in data["branches"] for p in data["products"])
        for branch, product in groups:
            key = (decision, branch, product)
            require(key in data["inventory"], f"Falta inventario al corte: {key}")
            forecast = baseline(data, decision, branch, product)
            inventory = data["inventory"][key]
            require(inventory["ingesta"] <= cutoff, "Inventario no disponible al corte")
            # Emisión al corte con información efectivamente disponible; baseline comprueba cada origen.
            used = [data["daily"][(decision - timedelta(days=i), branch, product)]["max_ingesta"] for i in range(7)]
            used += [data["inventory"][(decision - timedelta(days=i), branch, product)]["ingesta"] for i in range(7)]
            require(max(used) <= cutoff, "Características disponibles después del corte")
            forecast_id = f"M0_{decision.isoformat()}_{branch}_{product}_7d"
            forecast_rows.append({"pronostico_id": forecast_id, "fecha_emision": config["corte"], "sucursal_id": branch,
                                  "producto_id": product, "horizonte_dias": 7, "demanda_prevista": forecast,
                                  "modelo_version": "M0-1.0", "variables_version": "suma_7d-1.0", "corte_datos": config["corte"],
                                  "max_fecha_informacion": max(used).isoformat(), "universo": "demanda_libre_residual_sintetica"})
            transit = 0
            issues = []
            for order in data["orders"]:
                if (order["sucursal_id"], order["producto_id"]) != (branch, product):
                    continue
                pending = order["_ordered"] - order["_received"]
                reason = None
                if order["estado"] != "confirmado":
                    reason = "estado_" + order["estado"]
                elif not order["_confirmed"] or order["_arrival"] is None:
                    reason = "arribo_no_confirmado"
                    issues.append(reason)
                elif order["_arrival"] <= decision:
                    reason = "atrasado_sin_nuevo_arribo"
                    issues.append(reason)
                elif order["_arrival"] > decision + timedelta(days=7):
                    reason = "fuera_horizonte"
                if reason:
                    quality["pedidos_excluidos_transito"].append({"pedido_id": order["pedido_id"], "linea_id": order["linea_id"], "motivo": reason, "pendiente": pending})
                else:
                    transit += pending
            result = replenish(forecast, inventory["stock_cierre"], inventory["reservado"], transit, safety)
            # La cantidad es calculable; calendario y plazo de nuevas compras no están modelados.
            issues.append("revisar_calendario_y_plazo_nuevo_pedido")
            replenish_rows.append({"sucursal_id": branch, "producto_id": product, "fecha_decision": decision.isoformat(),
                                   "pronostico_id": forecast_id, "politica_version": policy["version"], "modo": config["modo"],
                                   "stock_cierre": inventory["stock_cierre"], "reservado": inventory["reservado"],
                                   **result, "estado": "REVISAR", "motivos": ";".join(issues)})

        close = [r for r in daily_rows if r["fecha"] == decision.isoformat()]
        net = sum((Decimal(r["ventas_netas"]) for r in close), Decimal(0))
        costs = sum((Decimal(r["costos"]) for r in close), Decimal(0))
        summary = {"caso": "RedNova reducido sintético", "fecha_cierre": decision.isoformat(),
                   "estado_datos": "COMPLETO_EN_ALCANCE_DIDACTICO", "estado_propuestas": "REVISAR",
                   "modo": config["modo"], "politica_version": policy["version"],
                   "lineas_cierre": sum(r["lineas"] for r in close), "unidades_cierre": sum(r["unidades"] for r in close),
                   "ventas_netas": money(net), "costos": money(costs), "margen": money(net - costs),
                   "margen_porcentaje": money(100 * (net - costs) / net) if net else None,
                   "grupos": len(groups), "dias_con_datos": len({r["fecha"] for r in daily_rows}),
                   "modelo_aprobado": "M0-1.0", "pedidos_emitidos": 0,
                   "alcance": "Una sucursal y tres productos; no es el panel anual de 12 sucursales/120 productos"}
        write_csv(out / "ventas_diarias.csv", daily_rows, list(daily_rows[0]))
        write_csv(out / "pronosticos.csv", forecast_rows, list(forecast_rows[0]))
        write_csv(out / "reposicion.csv", replenish_rows, list(replenish_rows[0]))
        write_json(out / "calidad.json", quality)
        write_json(out / "resumen.json", summary)
        report = ["# RedNova: resultado de la corrida", "", "Datos sintéticos. Propuestas provisionales sujetas a revisión humana.", "",
                  f"Cierre {decision}: {summary['lineas_cierre']} líneas, {summary['unidades_cierre']} unidades.",
                  f"Ventas {summary['ventas_netas']} UM; costos {summary['costos']} UM; margen {summary['margen']} UM ({summary['margen_porcentaje']}%).",
                  f"Política {policy['version']}; modo {config['modo']}; modelo M0-1.0.", "",
                  "|Producto|Pronóstico residual 7d|Disponible|Tránsito|Propuesta|Estado|", "|---|---:|---:|---:|---:|---|"]
        for row in replenish_rows:
            report.append(f"|{row['producto_id']}|{row['demanda_7d']}|{row['disponible']}|{row['transito_elegible']}|{row['propuesta_unidades']}|REVISAR|")
        report += ["", "Las recepciones ya están incorporadas al inventario; no se suman otra vez. Los pedidos excluidos constan en calidad.json.",
                   "El contrato sintético declara las reservas fuera de la demanda libre pronosticada. No extrapolar esta conciliación a fuentes reales.",
                   "Se necesita revisar calendario de arribos, plazo del nuevo pedido, mínimos, capacidad y presupuesto. No se emitió ningún pedido."]
        (out / "informe.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        manifest["estado"] = "COMPLETADA_CON_PROPUESTAS_PARA_REVISAR"
        for p in sorted(out.iterdir()):
            if p.is_file():
                manifest["archivos_salida_sha256"][p.name] = sha256(p)
        return summary
    except (ContractError, KeyError, OSError, ValueError, TypeError) as exc:
        manifest["estado"] = "BLOQUEADA"
        manifest["error"] = str(exc)
        # No se escriben productos finales hasta que todos los grupos han sido validados.
        write_json(out / "calidad.json", {"estado": "BLOQUEADA", "motivo": str(exc), "productos_finales_aceptados": False})
        raise ContractError(str(exc)) from exc
    finally:
        manifest["fin_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(out / "manifiesto.json", manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", default="datos")
    parser.add_argument("--config", default="config/ejecucion.json")
    parser.add_argument("--salida", required=True)
    args = parser.parse_args()
    try:
        summary = run(args.datos, args.config, args.salida)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (ContractError, OSError) as exc:
        print("BLOQUEADO: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
