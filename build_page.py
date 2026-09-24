"""Inyecta las existencias en la plantilla HTML y escribe una página autocontenida."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parent.parent / "templates" / "inventario.html"


def construir_pagina(articulos: list[dict], tienda: str, destino: Path,
                     modo_demo: bool = False) -> Path:
    datos = {
        "tienda": tienda,
        "actualizado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "demo": modo_demo,
        "articulos": articulos,
    }
    html = PLANTILLA.read_text(encoding="utf-8")
    html = html.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
    html = html.replace("__TIENDA__", tienda)
    destino.write_text(html, encoding="utf-8")
    return destino
