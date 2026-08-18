"""
MarkItDown Studio - Desktop Launcher
Launches the FastAPI backend and automatically opens the user's default browser.
Auto-detects virtual environment (.venv) if run with global Python.
"""

import sys
import os
import time
import argparse
import subprocess
import webbrowser
import threading
from pathlib import Path

def check_and_switch_venv(root_dir: Path):
    """If running from global Python and local .venv exists, re-launch using .venv python."""
    venv_win = root_dir / ".venv" / "Scripts" / "python.exe"
    venv_posix = root_dir / ".venv" / "bin" / "python"
    venv_python = venv_win if venv_win.exists() else (venv_posix if venv_posix.exists() else None)

    if venv_python and Path(sys.executable).resolve() != venv_python.resolve():
        print(f"[MarkItDown Studio] Activando entorno virtual local: {venv_python}")
        ret = subprocess.call([str(venv_python)] + sys.argv)
        sys.exit(ret)

def main():
    root_dir = Path(__file__).resolve().parent
    check_and_switch_venv(root_dir)

    parser = argparse.ArgumentParser(description="Start MarkItDown Studio Graphical Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    # Ensure current directory is in sys.path
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    try:
        import uvicorn
        from gui.app import app
    except ImportError as e:
        print(f"\n[Error] Faltan dependencias: {e}")
        print("Para instalar todas las dependencias necesarias ejecuta:")
        print("    pip install -r requirements-gui.txt\n")
        sys.exit(1)

    url = f"http://{args.host}:{args.port}"

    def open_browser():
        time.sleep(1.2)
        print(f"[MarkItDown Studio] Abriendo navegador en {url} ...")
        webbrowser.open(url)

    if not args.no_browser:
        threading.Thread(target=open_browser, daemon=True).start()

    print("\n" + "=" * 65)
    print(" 🚀  MarkItDown Studio — Universal Document to Markdown Engine")
    print("=" * 65)
    print(f" 🌐  Servidor Web UI listo en: {url}")
    print(" 📄  Formatos soportados: PDF, Word, Excel, PPT, Audio, Imágenes, etc.")
    print(" 💡  Presiona CTRL+C en esta terminal para detener el servidor.")
    print("=" * 65 + "\n")

    uvicorn.run(
        "gui.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )

if __name__ == "__main__":
    main()
