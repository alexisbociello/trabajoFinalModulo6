"""Pruebas de negocio y controles. Ejecutar: python -m unittest discover -s tests -v"""
import csv
import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.comun import ContractError, baseline, load_validated, replenish, timestamp
from src.entrenar import PERIODS, examples, metric, train
from src.pipeline import run

ROOT = Path(__file__).resolve().parents[1]


class RedNovaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)
        self.data = self.work / "datos"
        shutil.copytree(ROOT / "datos", self.data)
        self.cutoff = timestamp("2025-06-30T23:59:59Z")

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, filename):
        with (self.data / filename).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def save(self, filename, rows):
        with (self.data / filename).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_cierre_y_reposicion_reproducen_libro(self):
        out = self.work / "base"
        summary = run(self.data, ROOT / "config/ejecucion.json", out)
        self.assertEqual((summary["lineas_cierre"], summary["unidades_cierre"]), (3, 27))
        self.assertEqual([summary[k] for k in ("ventas_netas", "costos", "margen", "margen_porcentaje")],
                         ["2900.00", "2150.00", "750.00", "25.86"])
        with (out / "reposicion.csv").open() as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["producto_id"], "A100")
        self.assertEqual([row[k] for k in ("demanda_7d", "disponible", "transito_elegible", "propuesta_unidades")], ["140", "70", "40", "70"])
        self.assertEqual(row["estado"], "REVISAR")
        quality = json.loads((out / "calidad.json").read_text())
        self.assertIn("P004", [r["pedido_id"] for r in quality["pedidos_excluidos_transito"]])
        self.assertEqual(summary["pedidos_emitidos"], 0)

    def test_escenario_v2_aisla_politica(self):
        out = self.work / "v2"
        summary = run(self.data, ROOT / "config/escenario_v2.json", out)
        with (out / "reposicion.csv").open() as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["propuesta_unidades"], "90")
        self.assertEqual(summary["modo"], "contrafactual")
        self.assertEqual(summary["ventas_netas"], "2900.00")

    def test_cero_reposicion_es_distinto_de_faltante(self):
        result = replenish(35, 50, 0, 10, 2)
        self.assertEqual(result["propuesta_unidades"], 0)
        self.assertEqual(result["objetivo"], 45)

    def test_repeticion_no_sobrescribe_corrida(self):
        out = self.work / "misma"
        run(self.data, ROOT / "config/ejecucion.json", out)
        original = (out / "resumen.json").read_bytes()
        with self.assertRaisesRegex(ContractError, "ya existe"):
            run(self.data, ROOT / "config/ejecucion.json", out)
        self.assertEqual(original, (out / "resumen.json").read_bytes())

    def test_duplicado_exacto_se_registra_sin_sumarlo(self):
        rows = self.rows("ventas_lineas.csv")
        rows.append(dict(rows[-3]))
        self.save("ventas_lineas.csv", rows)
        data = load_validated(self.data, self.cutoff)
        self.assertEqual(len(data["quality"]["duplicados_exactos"]), 1)
        self.assertEqual(data["daily"][(date(2025, 6, 30), "S03", "A100")]["unidades"], 20)

    def test_id_conflictivo_bloquea(self):
        rows = self.rows("ventas_lineas.csv")
        modified = dict(rows[-1]); modified["cantidad"] = "3"; rows.append(modified)
        self.save("ventas_lineas.csv", rows)
        with self.assertRaisesRegex(ContractError, "conflictiva"):
            load_validated(self.data, self.cutoff)

    def test_maestro_duplicado_bloquea(self):
        rows = self.rows("productos.csv"); rows.append(dict(rows[0])); self.save("productos.csv", rows)
        with self.assertRaisesRegex(ContractError, "duplicada"):
            load_validated(self.data, self.cutoff)

    def test_costos_solapados_no_publican_total_parcial(self):
        rows = self.rows("costos_vigentes.csv")
        modified = dict(rows[0]); modified["desde"] = "2025-06-01"; modified["costo_unitario"] = "31"; rows.append(modified)
        self.save("costos_vigentes.csv", rows)
        out = self.work / "bloqueada"
        with self.assertRaisesRegex(ContractError, "solapados"):
            run(self.data, ROOT / "config/ejecucion.json", out)
        self.assertEqual(set(p.name for p in out.iterdir()), {"calidad.json", "manifiesto.json"})
        self.assertEqual(json.loads((out / "manifiesto.json").read_text())["estado"], "BLOQUEADA")

    def test_costo_ausente_bloquea(self):
        rows = [r for r in self.rows("costos_vigentes.csv") if r["producto_id"] != "B200"]
        self.save("costos_vigentes.csv", rows)
        with self.assertRaisesRegex(ContractError, "Costo ausente"):
            load_validated(self.data, self.cutoff)

    def test_reserva_mayor_stock_bloquea(self):
        rows = self.rows("inventario_diario.csv"); rows[-3]["reservado"] = "81"; self.save("inventario_diario.csv", rows)
        with self.assertRaisesRegex(ContractError, "Reserva mayor"):
            load_validated(self.data, self.cutoff)

    def test_inventario_faltante_no_es_cero(self):
        rows = self.rows("inventario_diario.csv"); del rows[-3]; self.save("inventario_diario.csv", rows)
        with self.assertRaisesRegex(ContractError, "Inventario faltante"):
            load_validated(self.data, self.cutoff)

    def test_dia_sin_ventas_ni_inventario_no_es_cero(self):
        sales = [r for r in self.rows("ventas_lineas.csv") if not r["fecha_evento"].startswith("2025-02-10")]
        inventory = [r for r in self.rows("inventario_diario.csv") if r["fecha"] != "2025-02-10"]
        self.save("ventas_lineas.csv", sales); self.save("inventario_diario.csv", inventory)
        with self.assertRaisesRegex(ContractError, "día faltante"):
            load_validated(self.data, self.cutoff)

    def test_venta_cero_requiere_lote_completo(self):
        rows = [r for r in self.rows("ventas_lineas.csv") if not (r["fecha_evento"].startswith("2025-02-10") and r["producto_id"] == "A100")]
        self.save("ventas_lineas.csv", rows)
        data = load_validated(self.data, self.cutoff)
        self.assertEqual(data["daily"][(date(2025, 2, 10), "S03", "A100")]["unidades"], 0)
        inv = self.rows("inventario_diario.csv")
        for row in inv:
            if row["fecha"] == "2025-02-10" and row["producto_id"] == "A100": row["ventas_completas"] = "false"
        self.save("inventario_diario.csv", inv)
        with self.assertRaisesRegex(ContractError, "incompleto"):
            load_validated(self.data, self.cutoff)

    def test_ingesta_tardia_no_se_filtra_como_cero(self):
        rows = self.rows("ventas_lineas.csv"); rows[-3]["fecha_ingesta"] = "2025-07-01T09:00:00Z"; self.save("ventas_lineas.csv", rows)
        with self.assertRaisesRegex(ContractError, "después del corte"):
            load_validated(self.data, self.cutoff)

    def test_quiebre_bloquea_baseline(self):
        rows = self.rows("inventario_diario.csv"); rows[-3]["quiebre"] = "true"; self.save("inventario_diario.csv", rows)
        data = load_validated(self.data, self.cutoff)
        with self.assertRaisesRegex(ContractError, "quiebre"):
            baseline(data, date(2025, 6, 30), "S03", "A100")

    def test_recepcion_inconsistente_bloquea(self):
        rows = self.rows("recepciones.csv"); rows[0]["cantidad"] = "11"; self.save("recepciones.csv", rows)
        with self.assertRaisesRegex(ContractError, "no concilian"):
            load_validated(self.data, self.cutoff)

    def test_metrica_cero_denominador(self):
        result = metric([{"real": 0, "M0": 4}], "M0")
        self.assertIsNone(result["WAPE_porcentaje"])
        self.assertEqual(result["MAE_unidades"], 4)

    def test_particiones_no_cruzan_fronteras_y_variables_no_futuras(self):
        rows = examples(load_validated(self.data, self.cutoff))
        for row in rows:
            start, end = PERIODS[row["particion"]]
            self.assertLessEqual(start.isoformat(), row["objetivo_desde"])
            self.assertLessEqual(row["objetivo_hasta"], end.isoformat())
            self.assertLess(row["fin_caracteristicas"], row["objetivo_desde"])
        self.assertTrue(all(row["objetivo_hasta"] <= "2025-03-31" for row in rows if row["particion"] == "entrenamiento"))

    def test_modelo_serializado_y_no_aprobado(self):
        out = self.work / "mlops"
        train(self.data, out)
        model = json.loads((out / "modelo_m1.json").read_text())
        self.assertEqual(model["estado"], "CANDIDATO_NO_APROBADO")
        self.assertEqual(model["ajustado_con_objetivos_hasta"], "2025-03-31")
        self.assertEqual(set(model["modelos_por_producto"]), {"A100", "B200", "C300"})


if __name__ == "__main__":
    unittest.main()
