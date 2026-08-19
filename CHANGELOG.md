# 🚀 MarkItDown Studio — Release v1.0.0

🎉 **Primera versión oficial de MarkItDown Studio.**

MarkItDown Studio es una interfaz gráfica moderna (Web GUI) y API REST construida sobre [Microsoft MarkItDown](https://github.com/microsoft/markitdown), diseñada para convertir cualquier documento, imagen, hoja de cálculo o audio a Markdown limpio con previsualización en tiempo real.

---

## ✨ Novedades y Características Principales

### 🎯 1. Conversión Universal Multi-Formato
- **Documentos**: PDF, Word (`.docx`, `.doc`), PowerPoint (`.pptx`, `.ppt`), EPub, Outlook (`.msg`).
- **Hojas de Cálculo y Datos**: Excel (`.xlsx`, `.xls`), CSV, JSON, XML, YAML.
- **Web y Código**: HTML, Markdown, Texto plano, Jupyter Notebooks (`.ipynb`).
- **Audio y Voz**: Transcripción de audio (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`).
- **Archivos Comprimidos**: ZIP (convierte el contenido empaquetado automáticamente).
- **URLs y YouTube**: Extracción de artículos web y transcripción completa de videos de YouTube.

### 🖼️ 2. Visión Multimodal & OCR Inteligente con OpenRouter / OpenAI
- Extracción precisa de texto, tablas, fechas y turnos médicos/horarios a partir de imágenes (`.png`, `.jpg`, `.jpeg`, `.webp`).
- Integración nativa y presets con **OpenRouter** (`openai/gpt-4o-mini`, `qwen/qwen-2-vl-72b-instruct`), **OpenAI** y **Ollama local** (`llava`, `llama3.2-vision`).
- Salida limpia en Markdown sin código residual en base64.

### 👁️ 3. Espacio de Trabajo Dual (Split View Workspace)
- **Modo Renderizado**: Previsualización HTML enriquecida con formateo de tablas, listas, citas y resaltado de sintaxis con *highlight.js*.
- **Modo Código (Raw Markdown)**: Editor de código fuente con tipografía monoespaciada para inspección directa.
- Alternador de vistas: *Pantalla Dividida (Side-by-Side)*, *Solo Previsualización*, *Solo Código*.

### 📦 4. Modo por Lotes (Batch Processing)
- Cola interactiva de archivos con indicador de estado individual.
- Procesamiento en streaming y botón de descarga de todas las conversiones en un único archivo comprimido **`.zip`**.

### 📊 5. Análisis y Métricas en Tiempo Real
- Conteo automático de palabras, caracteres y líneas.
- **Estimación de Tokens LLM** (para OpenAI GPT-4, Claude, DeepSeek, Llama).
- Medición de velocidad en milisegundos y tasa de tamaño in/out.

### 🎨 6. Diseño Glassmorphism Premium
- Paleta moderna con soporte de **Tema Oscuro** y **Tema Claro**.
- Botones de 1-clic para copiar al portapapeles y descargar en formato `.md` o `.html`.

### 🐳 7. Soporte para Docker & Docker Compose
- Despliegue con un solo comando: `docker compose up --build`.

### 🔌 8. Servidor MCP Nativo (Model Context Protocol)
- Integración directa para conectar con **Claude Desktop**, **Cursor**, **Gemini IDE / Antigravity**, **Cline** y **Roo Code**.
- Permite a los agentes de IA invocar herramientas para convertir documentos, imágenes con OCR y URLs directamente dentro de sus prompts.

---

## 🛠️ Instalación y Uso Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/euclides-ollarves/markitdown_studio.git
cd markitdown_studio

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\activate   # En Windows
pip install -r requirements.txt

# 3. Iniciar la aplicación
python run_gui.py
```
Accede en tu navegador a: `http://127.0.0.1:8000`

---

## 📄 Créditos
Desarrollado por **Euclides Ollarves** utilizando el motor de conversión [Microsoft MarkItDown](https://github.com/microsoft/markitdown).
