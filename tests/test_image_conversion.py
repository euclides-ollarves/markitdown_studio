"""
Test image conversion and metadata extraction
"""

import io
import sys
from pathlib import Path
from PIL import Image, ImageDraw

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gui.markitdown_service import MarkItDownService

def test_image_conversion():
    # Create a synthetic test PNG image
    img = Image.new("RGB", (640, 360), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 620, 340], outline=(99, 102, 241), width=4)
    draw.text((50, 50), "MarkItDown Test Document Image", fill=(255, 255, 255))

    stream = io.BytesIO()
    img.save(stream, format="PNG")
    img_bytes = stream.getvalue()

    service = MarkItDownService()
    out = service.convert_file(img_bytes, "screenshot_sample.png", "image/png")

    assert out.success, f"Image conversion failed: {out.error}"
    assert "screenshot_sample.png" in out.markdown
    assert "640 × 360" in out.markdown or "640" in out.markdown
    assert "data:image/png;base64" in out.markdown
    assert out.stats.word_count > 0

    print(f" [PASS] Image Conversion -> {out.stats.word_count} words in {out.stats.duration_ms}ms")
    print(f"\n--- Result Preview ---\n{out.markdown[:350]}...\n")

if __name__ == "__main__":
    test_image_conversion()
