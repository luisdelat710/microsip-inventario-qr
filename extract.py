"""Extracción de existencias: desde Firebird (Microsip) o desde un CSV de demo.

Ambas fuentes devuelven la misma estructura normalizada, así el resto del
pipeline no sabe (ni le importa) de dónde vienen los datos.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

SQL_PATH = Path(__file__).resolve().parent.parent / "sql" / "existencias.sql"

CATEGORIAS = ("PISO", "MURO", "ADHESIVO", "BOQUILLA")
RE_FORMATO = re.compile(r"(\d{2,3})\s*X\s*(\d{2,3})")
RE_M2 = re.compile(r"(\d+(?:\.\d+)?)\s*M2")


def normalizar(clave: str, nombre: str, unidad: str, existencia: float) -> dict:
    """Convierte una fila cruda de Microsip en un registro útil para la página.

    En Microsip el nombre del artículo trae casi toda la información
    (tipo, formato, calidad y m² por caja), así que se extrae de ahí.
    """
    nombre = " ".join(nombre.upper().split())
    categoria = next((c for c in CATEGORIAS if nombre.startswith(c)), "ACCESORIO")

    formato = RE_FORMATO.search(nombre)
    m2 = RE_M2.search(nombre)
    m2_caja = float(m2.group(1)) if m2 else None
    existencia = float(existencia or 0)

    if " 2DA" in nombre:
        calidad = "2da"
    elif " 1RA" in nombre:
        calidad = "1ra"
    else:
        calidad = None

    return {
        "clave": clave or "",
        "nombre": nombre,
        "categoria": categoria,
        "formato": f"{formato.group(1)}x{formato.group(2)}" if formato else None,
        "calidad": calidad,
        "unidad": (unidad or "PZA").upper(),
        "existencia": existencia,
        "m2_caja": m2_caja,
        "m2_total": round(existencia * m2_caja, 2) if m2_caja else None,
    }


def desde_csv(ruta: str | Path) -> list[dict]:
    """Modo demo: lee existencias de un CSV con columnas CLAVE,NOMBRE,UNIDAD,EXISTENCIA."""
    with open(ruta, newline="", encoding="utf-8") as f:
        return [
            normalizar(r["CLAVE"], r["NOMBRE"], r["UNIDAD"], r["EXISTENCIA"])
            for r in csv.DictReader(f)
        ]


def desde_firebird(cfg) -> list[dict]:
    """Modo real: consulta la base Firebird de Microsip con un usuario de solo lectura."""
    from firebird.driver import connect  # import tardío: el demo no lo necesita

    fb = cfg["firebird"]
    dsn = f"{fb['host']}/{fb.get('port', '3050')}:{fb['database']}"
    sql = SQL_PATH.read_text(encoding="utf-8")
    sql = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))

    with connect(dsn, user=fb["user"], password=fb["password"],
                 charset=fb.get("charset", "WIN1252")) as con:
        cur = con.cursor()
        cur.execute(sql, (int(cfg["tienda"]["almacen_id"]),))
        return [normalizar(*fila) for fila in cur.fetchall()]
