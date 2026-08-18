"""
Test full MarkItDown image OCR conversion with OpenRouter
"""

import io
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gui.markitdown_service import MarkItDownService

def test_openrouter_image_ocr():
    # 1. Create an image with clear text and a table-like schedule (like GUARDIAS)
    img = Image.new("RGB", (800, 450), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # Draw header and text
    draw.rectangle([30, 30, 770, 80], fill=(99, 102, 241))
    draw.text((50, 45), "ROL DE GUARDIAS - AGOSTO 2026", fill=(255, 255, 255))
    
    # Draw schedule items
    draw.text((50, 110), "Fecha: 18 de Agosto de 2026", fill=(15, 23, 42))
    draw.text((50, 140), "Turno Manana (08:00 - 16:00): Dr. Carlos Gomez, Lic. Maria Perez", fill=(15, 23, 42))
    draw.text((50, 170), "Turno Tarde  (16:00 - 24:00): Dra. Ana Torres, Lic. Juan Lopez", fill=(15, 23, 42))
    draw.text((50, 200), "Turno Noche  (00:00 - 08:00): Dr. Roberto Silva, Enf. Laura Diaz", fill=(15, 23, 42))
    draw.text((50, 250), "Notas: En caso de emergencia comunicarse a la extension 4402.", fill=(71, 85, 105))

    stream = io.BytesIO()
    img.save(stream, format="PNG")
    img_bytes = stream.getvalue()

    # 2. Test MarkItDown with OpenRouter
    service = MarkItDownService()
    
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    print("Running MarkItDown conversion with OpenRouter...")
    out = service.convert_file(
        file_bytes=img_bytes,
        filename="ROL_GUARDIAS.png",
        content_type="image/png",
        llm_api_key=api_key,
        llm_base_url=base_url,
        llm_model=model,
    )

    print(f"\nSuccess: {out.success}")
    print(f"Stats: {out.stats.word_count} words in {out.stats.duration_ms}ms")
    print(f"\n--- Output Markdown ---\n{out.markdown}\n")

if __name__ == "__main__":
    test_openrouter_image_ocr()
