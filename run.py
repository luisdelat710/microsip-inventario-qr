"""Pipeline completo: Microsip (Firebird) -> JSON -> HTML local -> QR.

Uso:
    python run.py --demo            # datos de ejemplo, sin Microsip
    python run.py                   # datos reales (requiere config.ini)
    python run.py --demo --serve    # además levanta el servidor en la red local
"""
from __future__ import annotations

import argparse
import configparser
import functools
import http.server
from pathlib import Path

from src.build_page import construir_pagina
from src.extract import desde_csv, desde_firebird
from src.make_qr import generar_qr, ip_local

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "output"


def main() -> None:
    p = argparse.ArgumentParser(description="Existencias de Microsip en una página local con QR")
    p.add_argument("--demo", action="store_true", help="usar sample_data/ en lugar de Firebird")
    p.add_argument("--serve", action="store_true", help="servir la página en la red local")
    args = p.parse_args()

    cfg = configparser.ConfigParser(inline_comment_prefixes=(";",))
    cfg.read(RAIZ / ("config.example.ini" if args.demo else "config.ini"), encoding="utf-8")
    if not args.demo and "firebird" not in cfg:
        raise SystemExit("Falta config.ini. Copia config.example.ini y llena tus datos, o usa --demo.")

    tienda = cfg.get("tienda", "nombre", fallback="Mi tienda")
    puerto = cfg.getint("tienda", "puerto_http", fallback=8000)

    articulos = (desde_csv(RAIZ / "sample_data" / "inventario_demo.csv")
                 if args.demo else desde_firebird(cfg))

    SALIDA.mkdir(exist_ok=True)
    pagina = construir_pagina(articulos, tienda, SALIDA / "index.html", modo_demo=args.demo)
    url = f"http://{ip_local()}:{puerto}/"
    qr = generar_qr(url, SALIDA / "qr.png")

    print(f"{len(articulos)} artículos -> {pagina}")
    print(f"QR -> {qr} ({url})")

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SALIDA))
        print(f"Sirviendo en {url}  (Ctrl+C para detener)")
        http.server.ThreadingHTTPServer(("0.0.0.0", puerto), handler).serve_forever()


if __name__ == "__main__":
    main()
