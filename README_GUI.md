# MarkItDown Studio — Graphical User Interface

Una interfaz gráfica moderna, rápida e intuitiva para el motor de conversión universal **[Microsoft MarkItDown](https://github.com/microsoft/markitdown)**.

![MarkItDown Studio](https://img.shields.io/badge/MarkItDown-Studio%20v1.0-6366f1)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)

---

## 🌟 Características Principales

- **Arrastrar y Soltar Inteligente (Drag & Drop)**: Soporte completo para **PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls), CSV, JSON, XML, HTML, Audio (.mp3, .wav), Imágenes (.png, .jpg), EPub, ZIP**.
- **Conversor de URLs & YouTube**: Extrae artículos de sitios web, páginas de Wikipedia y transcripciones completas de videos de YouTube directamente a Markdown.
- **Visor Dual de Markdown (Split View)**:
  - **Renderizado en Vivo**: Previsualización HTML con tablas formateadas, listas, encabezados y resaltado de sintaxis en bloques de código.
  - **Código Markdown Plano (Raw)**: Editor monospaciado con numeración y sintaxis.
  - Alternador de vista: *Pantalla dividida*, *Solo previsualización*, *Solo código*.
- **Métricas y Análisis en Tiempo Real**:
  - Conteo de palabras, caracteres y líneas.
  - **Estimación de Tokens LLM** (para OpenAI GPT-4, Claude, Llama).
  - Tiempo de procesamiento (ms) y ratio de compresión de tamaño.
- **Procesamiento por Lotes (Batch Mode)**:
  - Sube múltiples archivos a la vez.
  - Cola de conversión con barra de progreso interactiva.
  - Descarga individual o botón maestro de **"Descargar Todo en ZIP (.zip)"**.
- **Acciones Rápidas**:
  - Botón de **Copiar al Portapapeles** con un clic y feedback visual.
  - Descarga directa de archivos `.md` y `.html`.
- **Panel de Configuración de IA**:
  - Configuración opcional de API Key de OpenAI o endpoints locales (Ollama, vLLM, LMStudio en `http://localhost:11434/v1`) para OCR en imágenes y descripciones de audio.
  - Integración con Azure Content Understanding y Document Intelligence.
  - Soporte de plugins de MarkItDown.
- **Historial de Sesión**:
  - Acceso inmediato a las conversiones realizadas durante la sesión activa.
- **Diseño Glassmorphism Premium**:
  - Soporte para Tema Oscuro y Tema Claro con persistencia en el navegador.

---

## 🚀 Inicio Rápido

### 1. Requisitos
Tener instalado Python 3.10 o superior y las dependencias de la interfaz:

```bash
pip install -r requirements-gui.txt
```

### 2. Ejecutar la Interfaz Gráfica

Simplemente ejecuta el script lanzador:

```bash
python run_gui.py
```

*El navegador web se abrirá automáticamente en `http://127.0.0.1:8000`.*

### Parámetros opcionales del lanzador:
```bash
# Cambiar puerto
python run_gui.py --port 8080

# Iniciar sin abrir el navegador automáticamente
python run_gui.py --no-browser

# Modo desarrollo con auto-recarga
python run_gui.py --reload
```

---

## 🛠️ Estructura del Proyecto

```text
markitdown/
├── gui/
│   ├── __init__.py
│   ├── app.py                     # API FastAPI y servidor de archivos estáticos
│   ├── markitdown_service.py      # Wrapper del motor MarkItDown y cálculo de métricas
│   └── static/
│       ├── index.html             # Interfaz web responsiva
│       ├── css/
│       │   └── style.css          # Estilos CSS Glassmorphism y temas oscuro/claro
│       └── js/
│           └── app.js             # Lógica cliente (Marked, Highlight.js, JSZip, Toasts)
├── requirements-gui.txt           # Dependencias FastAPI, Uvicorn, python-multipart, httpx
├── run_gui.py                     # Lanzador de la aplicación con auto-apertura de navegador
├── tests/                         # Suite de pruebas automatizadas
│   ├── test_gui_conversion.py     # Pruebas de API y conversiones básicas
│   ├── test_xlsx_conversion.py    # Pruebas de Excel
│   └── test_docx_pptx.py          # Pruebas de PowerPoint
└── README_GUI.md                  # Documentación de la GUI
```

---

## 🧪 Ejecución de Pruebas

Para verificar que todos los conversores y endpoints funcionan correctamente:

```bash
python tests/test_gui_conversion.py
python tests/test_xlsx_conversion.py
python tests/test_docx_pptx.py
```
