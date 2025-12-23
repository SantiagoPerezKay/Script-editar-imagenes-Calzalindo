# Image Processor Watcher (Python + rembg + n8n)

Script en Python que observa una carpeta y procesa automáticamente las imágenes que se agregan: elimina fondo, centra el producto en un canvas 1080×1080, agrega un logo y duplica la imagen final según los códigos devueltos por un webhook de n8n.

Pensado para flujos de trabajo de e-commerce / ERP donde una imagen base debe replicarse para múltiples variantes (talles, colores, etc.).

---

## 🚀 Funcionalidades

- Observa una carpeta en tiempo real (Watchdog)
- Eliminación automática de fondo (`rembg`)
- Centrando inteligente sobre canvas 1080×1080
- Área útil de producto controlada (875 px)
- Inserción de logo en esquina superior derecha
- Comunicación con n8n vía webhook
- Duplicación de imágenes por código de artículo
- Compatible con ejecución como script (`.py`) o ejecutable (`.exe`)

---

## 📁 Estructura esperada

depurar_imagen/
│
├─ remover_fondo.py
├─ logo.png
├─ env/ # (opcional) entorno virtual
├─ fotos_editadas/
└─ README.md

yaml
Copiar código

---

## ⚙️ Requisitos

- Windows 11 (64 bits)
- Python 3.11.x
- Librerías:
  - numpy
  - pillow
  - rembg
  - watchdog
  - requests
  - pyinstaller (solo para compilar el ejecutable)

---

## 🧪 Instalación (modo desarrollo)

### 1. Crear entorno virtual (opcional pero recomendado)

python -m venv env
env\Scripts\activate

yaml
Copiar código

---

### 2. Instalar dependencias

pip install numpy pillow rembg watchdog requests

yaml
Copiar código

> Nota: `rembg` instala dependencias pesadas (onnxruntime). Es normal que demore.

---

## ▶️ Ejecución como script

python remover_fondo.py

yaml
Copiar código

El script queda observando la carpeta configurada:

WATCH_DIR = r"Z:\FOTOS\FOTOS_A_EDITAR"

yaml
Copiar código

Cada imagen nueva:
- Se procesa
- Se guarda en `fotos_editadas`
- Se duplica según los códigos devueltos por n8n

---

## 🔗 Integración con n8n

El script realiza un POST al webhook:

https://n8n.calzalindo.com.ar/webhook/imagen-procesada

css
Copiar código

Payload enviado:

```json
{
  "codigo": 134217
}
Respuesta esperada desde n8n:

json
Copiar código
[
  { "codigo": 134216 },
  { "codigo": 134217 },
  { "codigo": 134218 }
]
Cada codigo se utiliza para generar una copia de la imagen final.

🏗 Compilar a ejecutable (.exe)
1. Instalar PyInstaller
nginx
Copiar código
pip install pyinstaller
2. Compilar
csharp
Copiar código
pyinstaller --onefile --add-data "logo.png;." remover_fondo.py
El ejecutable se genera en:

bash
Copiar código
dist/remover_fondo.exe
🖼 Manejo correcto del logo en el ejecutable
Para que el logo funcione tanto en .py como en .exe, el script resuelve la ruta del recurso de esta forma:

python
Copiar código
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
Esto permite que PyInstaller empaquete correctamente logo.png.

🧠 Detalles técnicos
El nombre del archivo de salida respeta la lógica de nombres del ERP

Soporta artículos con múltiples variantes

Evita reprocesar imágenes ya existentes

Diseñado para ejecución continua (background process)

🛑 Consideraciones
El script debe tener permisos de escritura sobre la carpeta observada

El webhook de n8n debe responder JSON válido

El nombre del archivo de entrada debe ser numérico para ser procesado

📌 Autor / Uso
Proyecto desarrollado para automatización interna de procesamiento de imágenes.

Uso interno / empresarial.
