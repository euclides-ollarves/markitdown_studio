"""
MarkItDown Studio - Model Context Protocol (MCP) Server
Enables AI assistants (Claude Desktop, Cursor, Gemini IDE, Antigravity, Cline, Roo Code)
to convert any document, image, spreadsheet, audio, or web URL into clean Markdown.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

try:
    from mcp.server import MCPServer
except ImportError:
    from mcp.server.mcpserver import MCPServer

from gui.markitdown_service import MarkItDownService

# Initialize MCP Server
mcp = MCPServer(
    name="MarkItDown Studio",
    description="Universal Document to Markdown Converter with AI Vision OCR"
)

# Initialize MarkItDown Service
service = MarkItDownService()


@mcp.tool()
def convert_document(file_path: str) -> str:
    """
    Convert any local document (PDF, DOCX, XLSX, PPTX, CSV, JSON, XML, HTML, Audio, ZIP) into clean Markdown.

    Args:
        file_path: The absolute or relative path to the file to convert.

    Returns:
        The extracted and structured Markdown content of the document.
    """
    path = Path(file_path).resolve()
    if not path.exists() or not path.is_file():
        return f"Error: The file '{file_path}' does not exist or is not a valid file."

    try:
        with open(path, "rb") as f:
            file_bytes = f.read()

        result = service.convert_file(file_bytes, filename=path.name)
        if result.success:
            return result.markdown
        return f"Conversion Error: {result.error}"
    except Exception as e:
        return f"Failed to convert document '{file_path}': {str(e)}"


@mcp.tool()
def convert_image_ocr(image_path: str, custom_prompt: Optional[str] = None) -> str:
    """
    Extract and transcribe text, tables, forms, and schedules from an image into Markdown using Multimodal Vision OCR.

    Args:
        image_path: Path to the image file (.png, .jpg, .jpeg, .webp, .bmp).
        custom_prompt: Optional custom instruction for what specific information to extract or describe.

    Returns:
        Structured Markdown containing the transcribed text and data.
    """
    path = Path(image_path).resolve()
    if not path.exists() or not path.is_file():
        return f"Error: Image file '{image_path}' not found."

    try:
        with open(path, "rb") as f:
            file_bytes = f.read()

        result = service.convert_file(
            file_bytes=file_bytes,
            filename=path.name,
            llm_prompt=custom_prompt
        )
        if result.success:
            return result.markdown
        return f"OCR Error: {result.error}"
    except Exception as e:
        return f"Failed to extract text from image '{image_path}': {str(e)}"


@mcp.tool()
def convert_url(url: str) -> str:
    """
    Convert a web page article, documentation site, or YouTube video audio transcription into clean Markdown.

    Args:
        url: The web URL or YouTube link to convert.

    Returns:
        Clean Markdown representation of the page content or transcript.
    """
    try:
        result = service.convert_url(url)
        if result.success:
            return result.markdown
        return f"URL Conversion Error: {result.error}"
    except Exception as e:
        return f"Failed to convert URL '{url}': {str(e)}"


@mcp.tool()
def get_supported_formats() -> str:
    """
    Get the comprehensive list of all supported file extensions and document categories.

    Returns:
        A Markdown-formatted breakdown of all supported file formats.
    """
    formats = service.get_supported_formats()
    lines = ["# Supported Document Formats in MarkItDown Studio\n"]
    for category, exts in formats.items():
        lines.append(f"- **{category}**: `{'`, `'.join(exts)}`")
    return "\n".join(lines)


@mcp.tool()
def analyze_document_metrics(file_path: str) -> str:
    """
    Convert a document and return comprehensive statistics (word count, characters, lines, and estimated LLM tokens).

    Args:
        file_path: Path to the document file.

    Returns:
        JSON string containing word count, char count, estimated tokens, and processing duration.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return json.dumps({"error": f"File '{file_path}' not found"})

    try:
        with open(path, "rb") as f:
            file_bytes = f.read()

        result = service.convert_file(file_bytes, filename=path.name)
        if not result.success:
            return json.dumps({"error": result.error})

        stats = result.stats
        return json.dumps({
            "filename": path.name,
            "word_count": stats.word_count,
            "char_count": stats.char_count,
            "line_count": stats.line_count,
            "estimated_llm_tokens": stats.estimated_tokens,
            "processing_time_ms": stats.duration_ms,
            "input_size_bytes": stats.input_size_bytes,
            "output_size_bytes": stats.output_size_bytes,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def main():
    """Run the MCP server in stdio mode (default for LLM clients)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
