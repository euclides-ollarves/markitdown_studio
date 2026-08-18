"""
Test office document conversions (XLSX, etc.)
"""

import sys
import io
from pathlib import Path
import openpyxl

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gui.markitdown_service import MarkItDownService

def test_xlsx_conversion():
    # Create an in-memory workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Data"
    ws.append(["Region", "Q1 Sales", "Q2 Sales", "Growth"])
    ws.append(["North", 150000, 180000, "20%"])
    ws.append(["South", 90000, 110000, "22%"])
    ws.append(["West", 200000, 240000, "20%"])

    stream = io.BytesIO()
    wb.save(stream)
    xlsx_bytes = stream.getvalue()

    service = MarkItDownService()
    out = service.convert_file(xlsx_bytes, "quarterly_sales.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    assert out.success, f"XLSX conversion failed: {out.error}"
    assert "North" in out.markdown
    assert "Sales Data" in out.markdown or "Region" in out.markdown
    print(f" [PASS] XLSX Conversion -> {out.stats.word_count} words in {out.stats.duration_ms}ms")
    print(f" Preview:\n{out.markdown}\n")

if __name__ == "__main__":
    test_xlsx_conversion()
