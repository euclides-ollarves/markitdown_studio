"""
Test suite to verify MarkItDown GUI service and FastAPI endpoints
"""

import os
import sys
import io
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gui.markitdown_service import MarkItDownService
from fastapi.testclient import TestClient
from gui.app import app

def test_service_conversions():
    print("--> Testing MarkItDownService...")
    service = MarkItDownService()

    # 1. Test CSV Conversion
    csv_data = b"Product,Price,Quantity\nLaptop,1200,5\nMouse,25,40\nKeyboard,75,20\n"
    out_csv = service.convert_file(csv_data, "products.csv", "text/csv")
    assert out_csv.success, f"CSV conversion failed: {out_csv.error}"
    assert "Laptop" in out_csv.markdown
    assert out_csv.stats.word_count > 0
    print(f" [PASS] CSV Conversion: {out_csv.stats.word_count} words in {out_csv.stats.duration_ms}ms")

    # 2. Test JSON Conversion
    json_data = b'{"name": "MarkItDown Studio", "version": "1.0.0", "features": ["FastAPI", "Modern UI"]}'
    out_json = service.convert_file(json_data, "config.json", "application/json")
    assert out_json.success, f"JSON conversion failed: {out_json.error}"
    assert "MarkItDown Studio" in out_json.markdown
    print(f" [PASS] JSON Conversion: {out_json.stats.word_count} words in {out_json.stats.duration_ms}ms")

    # 3. Test HTML Conversion
    html_data = b"<html><head><title>Test Page</title></head><body><h1>Document Title</h1><p>This is a paragraph with <b>bold text</b>.</p></body></html>"
    out_html = service.convert_file(html_data, "index.html", "text/html")
    assert out_html.success, f"HTML conversion failed: {out_html.error}"
    assert "Document Title" in out_html.markdown
    print(f" [PASS] HTML Conversion: {out_html.stats.word_count} words in {out_html.stats.duration_ms}ms")

    # 4. Test Text Conversion
    txt_data = b"# Plain Text File\nThis is a simple test document.\n"
    out_txt = service.convert_file(txt_data, "notes.txt", "text/plain")
    assert out_txt.success, f"TXT conversion failed: {out_txt.error}"
    print(f" [PASS] TXT Conversion: {out_txt.stats.word_count} words in {out_txt.stats.duration_ms}ms")


def test_api_endpoints():
    print("\n--> Testing FastAPI REST Endpoints...")
    client = TestClient(app)

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    print(" [PASS] GET /api/health -> 200 OK")

    # 2. Supported Formats
    res = client.get("/api/supported-formats")
    assert res.status_code == 200
    formats = res.json()
    assert "Documents" in formats
    print(f" [PASS] GET /api/supported-formats -> {len(formats)} categories returned")

    # 3. POST /api/convert
    csv_bytes = io.BytesIO(b"Name,Role,City\nAlice,Engineer,Madrid\nBob,Designer,Barcelona\n")
    res = client.post(
        "/api/convert",
        files={"file": ("team.csv", csv_bytes, "text/csv")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "Alice" in data["markdown"]
    print(" [PASS] POST /api/convert -> Document converted successfully")

    # 4. POST /api/batch-convert
    f1 = ("doc1.csv", io.BytesIO(b"id,value\n1,Alpha\n"), "text/csv")
    f2 = ("doc2.json", io.BytesIO(b'{"key": "Beta"}'), "application/json")
    res = client.post(
        "/api/batch-convert",
        files=[("files", f1), ("files", f2)],
    )
    assert res.status_code == 200
    batch_data = res.json()
    assert batch_data["total_files"] == 2
    assert batch_data["successful_conversions"] == 2
    print(" [PASS] POST /api/batch-convert -> 2 files converted in batch")

    # 5. GET / serves HTML
    res = client.get("/")
    assert res.status_code == 200
    assert "MarkItDown Studio" in res.text
    print(" [PASS] GET / -> Index page served with title")

if __name__ == "__main__":
    test_service_conversions()
    test_api_endpoints()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
