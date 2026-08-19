import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from gui.markitdown_service import MarkItDownService
from mcp_server import mcp

app = FastAPI()

# Mount MCP SSE app directly
# sse_app has /sse and /messages
# If we mount at /mcp, endpoints are /mcp/sse and /mcp/messages
# If we mount at /sse_app, endpoints are /sse_app/sse and /sse_app/messages
sse_subapp = mcp.sse_app()
app.mount("/mcp", sse_subapp)

@app.get("/sse")
def get_sse_info():
    return {
        "status": "online",
        "name": "MarkItDown Studio MCP Server",
        "description": "Universal Document to Markdown Converter with Vision OCR",
        "endpoints": {
            "sse_stream": "/mcp/sse",
            "messages": "/mcp/messages",
            "full_sse_url": "http://<host>:8000/mcp/sse"
        },
        "tools": [
            "convert_document",
            "convert_image_ocr",
            "convert_url",
            "analyze_document_metrics",
            "get_supported_formats"
        ],
        "instructions": {
            "codex": "Use type 'HTTP secuenciable' with URL: http://<host>:8000/mcp/sse",
            "antigravity": "Add serverUrl: http://<host>:8000/mcp/sse in mcp_config.json"
        }
    }

client = TestClient(app)

# 1. Test browser friendly GET /sse
r1 = client.get("/sse")
print("GET /sse ->", r1.status_code, r1.json())

# 2. Test GET /mcp/sse with text/event-stream header (how Codex / MCP clients connect)
headers = {"Accept": "text/event-stream"}
r2 = client.get("/mcp/sse", headers=headers)
print("GET /mcp/sse ->", r2.status_code, r2.headers.get("content-type"))
