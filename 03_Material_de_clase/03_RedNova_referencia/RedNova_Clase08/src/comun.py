"""Contratos y cálculos del laboratorio RedNova. Solo biblioteca estándar."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path

VERSION = "rednova-practica-1.0.0"
SCHEMAS = {
    "ventas_lineas.csv": "venta_id,linea_id,fecha_evento,fecha_ingesta,sucursal_id,producto_id,cantidad,precio_unitario,descuento_linea",
    "inventario_diario.csv": "fecha,sucursal_id,producto_id,stock_cierre,reservado,quiebre,fecha_ingesta,ventas_completas",
    "productos.csv": "producto_id,nombre,categoria,activo",
    "sucursales.csv": "sucursal_id,nombre,region,activo",
    "costos_vigentes.csv": "producto_id,desde,hasta,costo_unitario,fecha_ingesta",
    "pedidos_abiertos.csv": "pedido_id,linea_id,sucursal_id,producto_id,cantidad_pedida,cantidad_recibida,estado,fecha_arribo,arribo_confirmado,fecha_ingesta",
    "recepciones.csv": "recepcion_id,linea_id,pedido_id,pedido_linea_id,sucursal_id,producto_id,fecha_evento,fecha_ingesta,cantidad",
}


class ContractError(ValueError):
    """Fallo de contrato: no se aceptan productos finales de esta corrida."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(result.tzinfo is not None, "Fecha sin zona horaria: " + value)
        return result.astimezone(timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ContractError("Fecha/hora inválida: " + str(value)) from exc


def day(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ContractError("Fecha inválida: " + str(value)) from exc


def integer(value, field, minimum=0):
    try:
        result = int(value)
        require(str(result) == str(value), f"{field}: entero canónico requerido, recibido {value!r}")
        require(result >= minimum, f"{field}: debe ser >= {minimum}")
        return result
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{field}: entero inválido {value!r}") from exc


def decimal(value, field, minimum=Decimal(0)):
    try:
        result = Decimal(str(value))
        require(result.is_finite() and result >= minimum, f"{field}: decimal no negativo y finito requerido")
        return result
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ContractError(f"{field}: decimal inválido {value!r}") from exc


def boolean(value, field):
    require(value in ("true", "false"), f"{field}: usar true o false")
    return value == "true"


def money(value):
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def ceil(value):
    return int(Decimal(value).to_integral_value(rounding=ROUND_CEILING))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_csv(root, filename):
    path = Path(root) / filename
    require(path.is_file(), f"Falta fuente obligatoria: {filename}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = SCHEMAS[filename].split(",")
        require(reader.fieldnames == expected, f"Esquema incompatible en {filename}; columnas esperadas: {','.join(expected)}")
        rows = list(reader)
    for number, row in enumerate(rows, 2):
        require(None not in row and None not in row.values(), f"Fila mal formada: {filename}:{number}")
    return rows


def unique(rows, keys, source, quality, allow_exact=False):
    seen = {}
    accepted = []
    for number, row in enumerate(rows, 2):
        key = tuple(row[k] for k in keys)
        require(all(key), f"Clave vacía en {source}:{number}")
        if key in seen:
            if allow_exact and row == seen[key]:
                quality["duplicados_exactos"].append({"fuente": source, "fila_csv": number, "clave": list(key)})
                continue
            raise ContractError(f"Clave duplicada/conflictiva en {source}: {key}")
        seen[key] = row
        accepted.append(row)
    return accepted


def load_validated(root, cutoff):
    """Carga, valida y agrega. Ante ambigüedad se bloquea toda la corrida didáctica."""
    root = Path(root)
    quality = {"estado": "VALIDO", "duplicados_exactos": [], "fuera_de_corte": [],
               "advertencias": [], "conteos": {}, "estrategia_fallo": "bloqueo_global_conservador"}
    require((root / "snapshot_fuentes.json").is_file(), "Falta snapshot_fuentes.json")
    snapshot = json.loads((root / "snapshot_fuentes.json").read_text(encoding="utf-8"))
    tables = {name: load_csv(root, name) for name in SCHEMAS}
    for name, rows in tables.items():
        quality["conteos"][name] = {"filas_leidas": len(rows)}
        declared_hash = snapshot.get("fuentes", {}).get(name, {}).get("sha256")
        if declared_hash and declared_hash != sha256(root / name):
            quality["advertencias"].append(f"{name} difiere de la huella del snapshot; es una variante de los datos originales")
    for name in ("productos.csv", "sucursales.csv"):
        known = snapshot.get("fuentes", {}).get(name, {}).get("disponibilidad")
        require(known and timestamp(known) <= cutoff, f"Maestro no disponible al corte: {name}")

    products = unique(tables["productos.csv"], ["producto_id"], "productos.csv", quality)
    branches = unique(tables["sucursales.csv"], ["sucursal_id"], "sucursales.csv", quality)
    require(products and branches, "Maestros vacíos")
    product_ids = {r["producto_id"] for r in products}
    branch_ids = {r["sucursal_id"] for r in branches}
    for source in (products, branches):
        for row in source:
            require(boolean(row["activo"], "activo"), "Esta práctica requiere maestros activos")

    def refs(row, source):
        require(row["producto_id"] in product_ids, f"Producto desconocido en {source}: {row['producto_id']}")
        if "sucursal_id" in row:
            require(row["sucursal_id"] in branch_ids, f"Sucursal desconocida en {source}")

    def available(rows, source):
        out = []
        for number, row in enumerate(rows, 2):
            ingested = timestamp(row["fecha_ingesta"])
            if "fecha_evento" in row:
                require(timestamp(row["fecha_evento"]) <= ingested, f"Ingesta anterior al evento: {source}:{number}")
            if ingested > cutoff:
                quality["fuera_de_corte"].append({"fuente": source, "fila_csv": number, "fecha_ingesta": row["fecha_ingesta"]})
            else:
                out.append(row)
        return out

    costs = available(tables["costos_vigentes.csv"], "costos_vigentes.csv")
    costs = unique(costs, ["producto_id", "desde"], "costos_vigentes.csv", quality)
    for row in costs:
        refs(row, "costos_vigentes.csv")
        row["_start"] = day(row["desde"])
        row["_end"] = day(row["hasta"]) if row["hasta"] else date.max
        row["_cost"] = decimal(row["costo_unitario"], "costo_unitario")
        require(row["_start"] < row["_end"], "Intervalo de costo vacío o invertido")
    for pid in product_ids:
        periods = sorted((r for r in costs if r["producto_id"] == pid), key=lambda r: r["_start"])
        for left, right in zip(periods, periods[1:]):
            require(left["_end"] <= right["_start"], f"Costos solapados para {pid}")

    sales = available(tables["ventas_lineas.csv"], "ventas_lineas.csv")
    sales = unique(sales, ["venta_id", "linea_id"], "ventas_lineas.csv", quality, allow_exact=True)
    daily = {}
    for row in sales:
        refs(row, "ventas_lineas.csv")
        when = timestamp(row["fecha_evento"]).date()
        q = integer(row["cantidad"], "cantidad", 1)
        p = decimal(row["precio_unitario"], "precio_unitario")
        discount = decimal(row["descuento_linea"], "descuento_linea")
        require(discount <= q * p, "Descuento superior al importe bruto")
        matching = [c for c in costs if c["producto_id"] == row["producto_id"] and c["_start"] <= when < c["_end"]]
        require(len(matching) == 1, f"Costo ausente o ambiguo para {row['producto_id']} en {when}")
        key = (when, row["sucursal_id"], row["producto_id"])
        item = daily.setdefault(key, {"unidades": 0, "ventas_netas": Decimal(0), "costos": Decimal(0), "lineas": 0, "max_ingesta": timestamp(row["fecha_ingesta"])})
        item["unidades"] += q
        item["ventas_netas"] += q * p - discount
        item["costos"] += q * matching[0]["_cost"]
        item["lineas"] += 1
        item["max_ingesta"] = max(item["max_ingesta"], timestamp(row["fecha_ingesta"]))
    quality["conteos"]["ventas_lineas.csv"]["filas_validas"] = len(sales)
    quality["cardinalidad"] = {"lineas_antes_union": len(sales), "lineas_despues_union": len(sales), "coincidencias_costo_por_linea": 1}

    inventories = available(tables["inventario_diario.csv"], "inventario_diario.csv")
    inventories = unique(inventories, ["fecha", "sucursal_id", "producto_id"], "inventario_diario.csv", quality)
    inv = {}
    for row in inventories:
        refs(row, "inventario_diario.csv")
        key = (day(row["fecha"]), row["sucursal_id"], row["producto_id"])
        require(key[0] <= timestamp(row["fecha_ingesta"]).date(), "Inventario fechado después de su ingesta")
        stock = integer(row["stock_cierre"], "stock_cierre")
        reserved = integer(row["reservado"], "reservado")
        require(reserved <= stock, "Reserva mayor que stock")
        inv[key] = {"stock_cierre": stock, "reservado": reserved, "quiebre": boolean(row["quiebre"], "quiebre"), "ventas_completas": boolean(row["ventas_completas"], "ventas_completas"), "ingesta": timestamp(row["fecha_ingesta"])}
        if key not in daily and inv[key]["ventas_completas"]:
            daily[key] = {"unidades": 0, "ventas_netas": Decimal(0), "costos": Decimal(0), "lineas": 0, "max_ingesta": inv[key]["ingesta"]}
    for key in daily:
        require(key in inv, f"Inventario faltante para {key}")
        require(inv[key]["ventas_completas"], f"Lote de ventas incompleto para {key}")
    first_day = day(snapshot["periodo_ventas_desde"])
    last_day = min(day(snapshot["periodo_ventas_hasta"]), cutoff.date())
    current = first_day
    while current <= last_day:
        for branch in branch_ids:
            for product in product_ids:
                key = (current, branch, product)
                require(key in inv, f"Inventario o día faltante en la grilla declarada: {key}")
                require(inv[key]["ventas_completas"], f"Lote de ventas incompleto para {key}")
        current += timedelta(days=1)
    for row in tables["ventas_lineas.csv"]:
        if timestamp(row["fecha_ingesta"]) > cutoff and timestamp(row["fecha_evento"]).date() <= last_day:
            raise ContractError("Hay ventas de la ventana declarada ingresadas después del corte; revisar completitud sin imputar cero")
    require(daily, "No hay datos diarios utilizables")

    orders = available(tables["pedidos_abiertos.csv"], "pedidos_abiertos.csv")
    orders = unique(orders, ["pedido_id", "linea_id"], "pedidos_abiertos.csv", quality)
    order_index = {}
    for row in orders:
        refs(row, "pedidos_abiertos.csv")
        row["_ordered"] = integer(row["cantidad_pedida"], "cantidad_pedida", 1)
        row["_received"] = integer(row["cantidad_recibida"], "cantidad_recibida")
        require(row["_received"] <= row["_ordered"], "Cantidad recibida mayor que pedida")
        require(row["estado"] in {"confirmado", "cancelado", "pendiente"}, "Estado de pedido desconocido")
        row["_confirmed"] = boolean(row["arribo_confirmado"], "arribo_confirmado")
        row["_arrival"] = day(row["fecha_arribo"]) if row["fecha_arribo"] else None
        order_index[(row["pedido_id"], row["linea_id"])] = row
    receipts = available(tables["recepciones.csv"], "recepciones.csv")
    receipts = unique(receipts, ["recepcion_id", "linea_id"], "recepciones.csv", quality, allow_exact=True)
    received_totals = {}
    for row in receipts:
        refs(row, "recepciones.csv")
        key = (row["pedido_id"], row["pedido_linea_id"])
        require(key in order_index, "Recepción sin pedido conocido")
        order = order_index[key]
        require(row["producto_id"] == order["producto_id"] and row["sucursal_id"] == order["sucursal_id"], "Recepción y pedido no coinciden en producto/sucursal")
        received_totals[key] = received_totals.get(key, 0) + integer(row["cantidad"], "cantidad recepción", 1)
    for key, order in order_index.items():
        require(received_totals.get(key, 0) == order["_received"], f"Recepciones no concilian con recibido acumulado: {key}")

    return {"daily": daily, "inventory": inv, "orders": orders, "quality": quality,
            "products": products, "branches": branches, "snapshot": snapshot, "sales": sales}


def baseline(data, origin, branch, product):
    values = []
    as_of = datetime.combine(origin, datetime.max.time(), tzinfo=timezone.utc)
    for offset in range(6, -1, -1):
        key = (origin - timedelta(days=offset), branch, product)
        require(key in data["daily"] and key in data["inventory"], f"M0 necesita siete días completos: falta {key}")
        inventory = data["inventory"][key]
        require(inventory["ventas_completas"] and not inventory["quiebre"], f"M0 no aplicable por lote incompleto/quiebre: {key}")
        require(data["daily"][key]["max_ingesta"] <= as_of and inventory["ingesta"] <= as_of, f"Información no disponible al origen {origin}")
        values.append(data["daily"][key]["unidades"])
    return sum(values)


def replenish(forecast, stock, reserved, transit, safety_days, horizon=7):
    forecast = decimal(forecast, "demanda residual")
    require(reserved <= stock, "Reserva mayor que stock")
    safety = ceil(forecast / horizon * safety_days)
    target = ceil(forecast + safety)
    available = stock - reserved
    return {"demanda_7d": str(forecast), "disponible": available, "transito_elegible": transit,
            "seguridad_unidades": safety, "objetivo": target,
            "propuesta_unidades": max(0, target - available - transit)}
