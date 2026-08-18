"""
MarkItDown Service Wrapper
Provides robust conversion capabilities for single files, batches, and URLs,
with integrated OpenRouter / OpenAI vision models for image OCR and document extraction.
"""

import io
import os
import sys
import time
import math
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass

from PIL import Image, ExifTags
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Ensure markitdown package can be imported from local repository if needed
current_dir = Path(__file__).resolve().parent
repo_pkg = current_dir.parent / "markitdown" / "packages" / "markitdown" / "src"
if repo_pkg.exists() and str(repo_pkg) not in sys.path:
    sys.path.insert(0, str(repo_pkg))

try:
    from markitdown import MarkItDown, StreamInfo
    from markitdown._base_converter import DocumentConverterResult
except ImportError:
    from markitdown import MarkItDown, StreamInfo  # type: ignore
    from markitdown._base_converter import DocumentConverterResult  # type: ignore


# Default OpenRouter Vision integration fallback
DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}


@dataclass
class ConversionStats:
    char_count: int
    word_count: int
    line_count: int
    estimated_tokens: int
    duration_ms: float
    input_size_bytes: int
    output_size_bytes: int


@dataclass
class ConversionOutput:
    success: bool
    filename: str
    markdown: str
    title: Optional[str]
    stats: ConversionStats
    error: Optional[str] = None
    mimetype: Optional[str] = None


class MarkItDownService:
    """Service to handle document conversions using Microsoft MarkItDown and OpenRouter Vision."""

    SUPPORTED_EXTENSIONS = {
        "Documents": [".pdf", ".docx", ".doc", ".pptx", ".ppt", ".epub", ".msg"],
        "Spreadsheets & Data": [".xlsx", ".xls", ".csv", ".json", ".xml", ".yaml", ".yml"],
        "Web & Code": [".html", ".htm", ".txt", ".md", ".rst", ".ipynb"],
        "Images (OCR/Vision)": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"],
        "Audio (Transcription)": [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
        "Archives": [".zip"],
    }

    def __init__(self):
        self._default_instance = self._create_instance()

    def _resolve_llm_credentials(
        self,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> tuple[str, str, str]:
        """Resolve LLM credentials with fallback to default OpenRouter settings."""
        key = (llm_api_key or "").strip() or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        base = (llm_base_url or "").strip() or os.getenv("OPENROUTER_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEFAULT_OPENROUTER_BASE
        model = (llm_model or "").strip() or os.getenv("OPENROUTER_MODEL") or os.getenv("OPENAI_MODEL") or DEFAULT_OPENROUTER_MODEL
        return key, base, model

    def _create_instance(
        self,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_prompt: Optional[str] = None,
        cu_endpoint: Optional[str] = None,
        cu_analyzer_id: Optional[str] = None,
        docintel_endpoint: Optional[str] = None,
        enable_plugins: bool = True,
    ) -> MarkItDown:
        """Create a configured MarkItDown instance with OpenRouter / LLM Vision."""
        key, base, model = self._resolve_llm_credentials(llm_api_key, llm_base_url, llm_model)

        kwargs: Dict[str, Any] = {
            "enable_builtins": True,
            "enable_plugins": enable_plugins,
        }

        if key or base:
            try:
                from openai import OpenAI
                client_kwargs: Dict[str, Any] = {"api_key": key or "dummy-key"}
                if base:
                    client_kwargs["base_url"] = base
                if "openrouter.ai" in (base or ""):
                    client_kwargs["default_headers"] = {
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "MarkItDown Studio",
                    }

                kwargs["llm_client"] = OpenAI(**client_kwargs)
                kwargs["llm_model"] = model
                kwargs["llm_prompt"] = llm_prompt or (
                    "Transcribe all text, numbers, schedules, and tables from this image into clean Markdown. "
                    "Preserve headers, lists, and formatting. Do not include markdown code block backticks around the whole output."
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize LLM client: {e}")

        if cu_endpoint:
            kwargs["cu_endpoint"] = cu_endpoint
            if cu_analyzer_id:
                kwargs["cu_analyzer_id"] = cu_analyzer_id

        if docintel_endpoint:
            kwargs["docintel_endpoint"] = docintel_endpoint

        return MarkItDown(**kwargs)

    def _ocr_image_directly(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_prompt: Optional[str] = None,
    ) -> str:
        """Directly call Vision model on OpenRouter for ultra-precise text & OCR extraction."""
        key, base, model = self._resolve_llm_credentials(llm_api_key, llm_base_url, llm_model)
        
        mime = content_type or mimetypes.guess_type(filename)[0] or "image/png"
        b64_img = base64.b64encode(file_bytes).decode("utf-8")
        data_uri = f"data:{mime};base64,{b64_img}"

        prompt = llm_prompt or (
            "Transcribe and extract ALL text, tables, forms, dates, lists, and data from this image into clean, structured Markdown. "
            "Maintain the exact layout and hierarchy (headings, bullet points, table columns). "
            "If the image has no readable text, describe the visual content in detail."
        )

        from openai import OpenAI
        client_kwargs: Dict[str, Any] = {"api_key": key or "dummy-key"}
        if base:
            client_kwargs["base_url"] = base
        if "openrouter.ai" in (base or ""):
            client_kwargs["default_headers"] = {
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "MarkItDown Studio",
            }

        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            max_tokens=2048,
        )
        
        result_text = response.choices[0].message.content or ""
        # Clean up any surrounding ```markdown blocks if present
        cleaned = result_text.strip()
        if cleaned.startswith("```markdown"):
            cleaned = cleaned[11:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def calculate_stats(self, markdown_text: str, input_size: int, duration_ms: float) -> ConversionStats:
        """Compute document metrics including word count, lines, and LLM tokens estimate."""
        char_count = len(markdown_text)
        words = markdown_text.split()
        word_count = len(words)
        line_count = len(markdown_text.splitlines()) if markdown_text else 0
        estimated_tokens = max(1, math.ceil(char_count / 4)) if char_count > 0 else 0
        output_size_bytes = len(markdown_text.encode("utf-8"))

        return ConversionStats(
            char_count=char_count,
            word_count=word_count,
            line_count=line_count,
            estimated_tokens=estimated_tokens,
            duration_ms=round(duration_ms, 2),
            input_size_bytes=input_size,
            output_size_bytes=output_size_bytes,
        )

    def convert_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_prompt: Optional[str] = None,
        cu_endpoint: Optional[str] = None,
        cu_analyzer_id: Optional[str] = None,
        docintel_endpoint: Optional[str] = None,
        enable_plugins: bool = True,
    ) -> ConversionOutput:
        """Convert a file from memory bytes to Markdown."""
        start_time = time.perf_counter()
        input_size = len(file_bytes)
        ext = Path(filename).suffix.lower() if filename else ""
        is_image = ext in IMAGE_EXTENSIONS or (content_type and content_type.startswith("image/"))

        try:
            if is_image:
                # Direct vision OCR via OpenRouter
                markdown_content = self._ocr_image_directly(
                    file_bytes=file_bytes,
                    filename=filename,
                    content_type=content_type,
                    llm_api_key=llm_api_key,
                    llm_base_url=llm_base_url,
                    llm_model=llm_model,
                    llm_prompt=llm_prompt,
                )
                title = Path(filename).stem
            else:
                md_instance = self._create_instance(
                    llm_api_key=llm_api_key,
                    llm_base_url=llm_base_url,
                    llm_model=llm_model,
                    llm_prompt=llm_prompt,
                    cu_endpoint=cu_endpoint,
                    cu_analyzer_id=cu_analyzer_id,
                    docintel_endpoint=docintel_endpoint,
                    enable_plugins=enable_plugins,
                )

                file_stream = io.BytesIO(file_bytes)
                stream_info = StreamInfo(
                    filename=filename,
                    extension=ext,
                    mimetype=content_type or "",
                )

                result: DocumentConverterResult = md_instance.convert_stream(
                    file_stream,
                    stream_info=stream_info,
                )

                markdown_content = (result.markdown or "").strip()
                title = result.title or Path(filename).stem

            duration_ms = (time.perf_counter() - start_time) * 1000
            stats = self.calculate_stats(markdown_content, input_size, duration_ms)

            return ConversionOutput(
                success=True,
                filename=filename,
                markdown=markdown_content,
                title=title,
                stats=stats,
                mimetype=content_type,
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            stats = self.calculate_stats("", input_size, duration_ms)
            return ConversionOutput(
                success=False,
                filename=filename,
                markdown="",
                title=filename,
                stats=stats,
                error=str(e),
                mimetype=content_type,
            )

    def convert_url(
        self,
        url: str,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> ConversionOutput:
        """Convert a web URL or YouTube link to Markdown."""
        start_time = time.perf_counter()
        try:
            md_instance = self._create_instance(
                llm_api_key=llm_api_key,
                llm_base_url=llm_base_url,
                llm_model=llm_model,
            )

            result = md_instance.convert_url(url)
            duration_ms = (time.perf_counter() - start_time) * 1000
            markdown_content = result.markdown or ""
            title = result.title or url

            stats = self.calculate_stats(markdown_content, len(url.encode("utf-8")), duration_ms)

            return ConversionOutput(
                success=True,
                filename=url,
                markdown=markdown_content,
                title=title,
                stats=stats,
                mimetype="text/html",
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            stats = self.calculate_stats("", len(url.encode("utf-8")), duration_ms)
            return ConversionOutput(
                success=False,
                filename=url,
                markdown="",
                title=url,
                stats=stats,
                error=str(e),
                mimetype="text/html",
            )

    @classmethod
    def get_supported_formats(cls) -> Dict[str, List[str]]:
        """Return categorization of all supported file extensions."""
        return cls.SUPPORTED_EXTENSIONS
