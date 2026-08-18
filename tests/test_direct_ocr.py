"""
Direct OCR and MarkItDown Image Service test
"""

import io
import sys
import base64
from pathlib import Path
from PIL import Image, ImageDraw

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gui.markitdown_service import MarkItDownService

# Create test image
img = Image.new("RGB", (700, 300), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((30, 30), "TURNO MEDICO DE GUARDIAS", fill=(0, 0, 0))
draw.text((30, 80), "Doctor: Roberto Gomez - Area: Urgencias", fill=(0, 0, 0))
draw.text((30, 130), "Horario: 08:00 a 20:00 hrs", fill=(0, 0, 0))

stream = io.BytesIO()
img.save(stream, format="PNG")
img_bytes = stream.getvalue()

service = MarkItDownService()
# Test without passing any parameters (should use server default OpenRouter!)
out = service.convert_file(img_bytes, "test_guardia.png", "image/png")

print(f"Success: {out.success}")
print(f"Stats: {out.stats.word_count} words in {out.stats.duration_ms}ms")
print(f"\n--- Markdown Result ---\n{out.markdown}\n")
