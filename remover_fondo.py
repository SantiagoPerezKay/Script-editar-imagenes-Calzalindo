import time
import os
import io
import numpy as np
import requests
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rembg import remove
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
# =========================
# CONFIG
# =========================

WATCH_DIR = r"Z:\FOTOS\FOTOS_A_EDITAR"
OUTPUT_DIR = os.path.join(WATCH_DIR, "fotos_editadas")

EXT_PERMITIDAS = (".jpg", ".jpeg", ".png", ".webp")

CANVAS_SIZE = 1080
AREA_UTIL = 875

LOGO_PATH = resource_path("logo.png")
LOGO_MAX_WIDTH = 320
LOGO_MARGIN = 40

N8N_WEBHOOK = "https://n8n.calzalindo.com.ar/webhook/imagen-procesada"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
# =========================
# IMAGEN
# =========================

def centrar_en_1080(img):
    arr = np.array(img)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 0)

    if len(xs) == 0:
        return Image.new("RGB", (1080, 1080), (255, 255, 255))

    recorte = img.crop((xs.min(), ys.min(), xs.max(), ys.max()))

    ratio = min(AREA_UTIL / recorte.width, AREA_UTIL / recorte.height)
    recorte = recorte.resize(
        (int(recorte.width * ratio), int(recorte.height * ratio)),
        Image.LANCZOS
    )

    canvas = Image.new("RGB", (1080, 1080), (255, 255, 255))
    canvas.paste(
        recorte,
        ((1080 - recorte.width) // 2, (1080 - recorte.height) // 2),
        recorte
    )
    return canvas


def agregar_logo(img):
    print("Buscando logo en:", os.path.abspath(LOGO_PATH))
    if not os.path.exists(LOGO_PATH):
        return img

    logo = Image.open(LOGO_PATH).convert("RGBA")
    ratio = LOGO_MAX_WIDTH / logo.width
    logo = logo.resize((LOGO_MAX_WIDTH, int(logo.height * ratio)), Image.LANCZOS)

    img.paste(
        logo,
        (1080 - logo.width - LOGO_MARGIN, LOGO_MARGIN),
        logo
    )
    return img

# =========================
# N8N
# =========================

def obtener_codigos(codigo):
    resp = requests.post(
        "https://n8n.calzalindo.com.ar/webhook/imagen-procesadas",
        json={"codigo": codigo},
        timeout=10
    )

    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        print("⚠ Respuesta inesperada de n8n:", data)
        return []

    return [int(item["codigo"]) for item in data if "codigo" in item]


# =========================
# DUPLICAR
# =========================

def duplicar_imagen(origen, codigos):
    for c in codigos:
        nombre_dup = construir_nombre_imagen(c)
        destino = os.path.join(OUTPUT_DIR, nombre_dup)
        if not os.path.exists(destino):
            with open(origen, "rb") as src, open(destino, "wb") as dst:
                dst.write(src.read())

# =========================
# MAIN
# =========================

def procesar_imagen(path):
    nombre = os.path.basename(path)
    codigo_txt = os.path.splitext(nombre)[0]

    if not codigo_txt.isdigit():
        return

    codigo = int(codigo_txt)
    nombre_salida = construir_nombre_imagen(codigo)
    salida = os.path.join(OUTPUT_DIR, nombre_salida)

    if os.path.exists(salida):
        return

    try:
        img_bytes = open(path, "rb").read()
        result = remove(img_bytes)

        img = Image.open(io.BytesIO(result)).convert("RGBA")
        img = centrar_en_1080(img)
        img = agregar_logo(img)

        img.save(salida, "JPEG", quality=95, optimize=True)

        codigos = obtener_codigos(codigo)
        duplicar_imagen(salida, codigos)

        print(f"✔ {codigo} → {codigos}")

    except Exception as e:
        print(f"✖ Error {nombre}: {e}")
# =========================
# construir imagen
# =========================
def construir_nombre_imagen(numero, orden=1):
    empresa = "0001"
    tipo = "AR"
    sistema = "0000000"
    pre="000"
    numero_fmt = str(numero).zfill(16)
    orden_fmt = str(orden).zfill(6)

    return f"{empresa}{tipo}{sistema}-{pre}{numero_fmt}{orden_fmt}.jpg"

# =========================
# WATCHDOG
# =========================

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(EXT_PERMITIDAS):
            time.sleep(1)
            procesar_imagen(event.src_path)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()

    observer = Observer()
    observer.schedule(Handler(), WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
