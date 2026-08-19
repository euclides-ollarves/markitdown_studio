"""
FastAPI Server for MarkItDown Studio
Exposes REST endpoints for single-file, batch, and URL document conversions,
and serves the modern reactive Web GUI.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .markitdown_service import MarkItDownService, ConversionOutput

app = FastAPI(
    title="MarkItDown Studio API",
    description="Graphical and REST interface for Microsoft MarkItDown document conversion",
    version="1.0.0",
)

# CORS Middleware to support any local integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = MarkItDownService()

# Mount MCP SSE Server for remote AI Clients (Codex, OpenCode, Cursor, Claude Desktop, Antigravity)
try:
    from mcp_server import mcp as mcp_server_instance
    from mcp.server.transport_security import TransportSecuritySettings
    # Allow remote network IPs (e.g. 192.168.1.97) and custom domains without 421 Invalid Host header
    security_settings = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    app.mount("/mcp", mcp_server_instance.sse_app(transport_security=security_settings))
    print("[MCP] Servidor MCP SSE montado en /mcp/sse (Acceso por IP de red local y remota habilitado)")
except Exception as e:
    print(f"[Warning] No se pudo montar el servidor MCP SSE: {e}")

@app.get("/sse")
@app.get("/mcp")
async def mcp_info():
    """Information endpoint for MCP server status and client connection details."""
    return {
        "status": "online",
        "service": "MarkItDown Studio MCP Server",
        "protocol": "Model Context Protocol (MCP)",
        "transport": "SSE (Server-Sent Events)",
        "sse_endpoint": "/mcp/sse",
        "messages_endpoint": "/mcp/messages",
        "tools": [
            "convert_document",
            "convert_image_ocr",
            "convert_url",
            "analyze_document_metrics",
            "get_supported_formats"
        ],
        "connection_guide": {
            "codex": "Selecciona 'HTTP secuenciable' e ingresa la URL: http://<host>:8000/mcp/sse",
            "antigravity": "Configura serverUrl: http://<host>:8000/mcp/sse en mcp_config.json",
            "cursor": "Configura serverUrl: http://<host>:8000/mcp/sse en .cursor/mcp.json"
        }
    }

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class UrlConversionRequest(BaseModel):
    url: str
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "MarkItDown Studio", "version": "1.0.0"}


@app.get("/api/supported-formats")
async def get_supported_formats():
    """Return categorized list of supported file formats and extensions."""
    return service.get_supported_formats()


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    llm_api_key: Optional[str] = Form(None),
    llm_base_url: Optional[str] = Form(None),
    llm_model: Optional[str] = Form(None),
    llm_prompt: Optional[str] = Form(None),
    cu_endpoint: Optional[str] = Form(None),
    cu_analyzer_id: Optional[str] = Form(None),
    docintel_endpoint: Optional[str] = Form(None),
    enable_plugins: bool = Form(True),
):
    """Convert a single uploaded document to Markdown."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        output: ConversionOutput = service.convert_file(
            file_bytes=content,
            filename=file.filename or "document",
            content_type=file.content_type,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            llm_prompt=llm_prompt,
            cu_endpoint=cu_endpoint,
            cu_analyzer_id=cu_analyzer_id,
            docintel_endpoint=docintel_endpoint,
            enable_plugins=enable_plugins,
        )

        return asdict(output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert-url")
async def convert_url(request: UrlConversionRequest):
    """Convert a web page or YouTube URL to Markdown."""
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    output: ConversionOutput = service.convert_url(
        url=request.url.strip(),
        llm_api_key=request.llm_api_key,
        llm_base_url=request.llm_base_url,
        llm_model=request.llm_model,
    )
    return asdict(output)


@app.post("/api/batch-convert")
async def batch_convert(
    files: List[UploadFile] = File(...),
    llm_api_key: Optional[str] = Form(None),
    llm_base_url: Optional[str] = Form(None),
    llm_model: Optional[str] = Form(None),
    enable_plugins: bool = Form(True),
):
    """Convert multiple files in a single batch request."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch conversion.")

    results: List[dict] = []
    for file in files:
        try:
            content = await file.read()
            out = service.convert_file(
                file_bytes=content,
                filename=file.filename or "document",
                content_type=file.content_type,
                llm_api_key=llm_api_key,
                llm_base_url=llm_base_url,
                llm_model=llm_model,
                enable_plugins=enable_plugins,
            )
            results.append(asdict(out))
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename or "unknown",
                "markdown": "",
                "title": file.filename or "unknown",
                "stats": {
                    "char_count": 0,
                    "word_count": 0,
                    "line_count": 0,
                    "estimated_tokens": 0,
                    "duration_ms": 0,
                    "input_size_bytes": 0,
                    "output_size_bytes": 0,
                },
                "error": str(e),
                "mimetype": file.content_type,
            })

    return {
        "total_files": len(files),
        "successful_conversions": sum(1 for r in results if r["success"]),
        "results": results,
    }


# Mount static assets if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve main application interface."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>MarkItDown Studio UI is starting...</h1>")
