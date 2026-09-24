"""Genera el QR que apunta a la página de existencias dentro de la red local."""
from __future__ import annotations

import socket
from pathlib import Path

import qrcode


def ip_local() -> str:
    """IP de esta PC en la red de la tienda (no envía datos, solo resuelve la ruta)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def generar_qr(url: str, destino: Path) -> Path:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=12, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="#1B3A63", back_color="white").save(destino)
    return destino
