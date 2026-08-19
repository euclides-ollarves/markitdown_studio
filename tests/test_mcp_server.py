"""
Test MCP Server Tools and Functions
"""

import os
import sys
import json
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from mcp_server import (
    convert_document,
    convert_image_ocr,
    convert_url,
    get_supported_formats,
    analyze_document_metrics
)

def test_mcp_tools():
    print("--> Testing MCP Tools...")

    # 1. Test get_supported_formats
    formats_md = get_supported_formats()
    assert "PDF" in formats_md or "Documents" in formats_md
    print(" [PASS] get_supported_formats()")

    # 2. Test convert_document with a sample file
    sample_file = root_dir / "README.md"
    res_md = convert_document(str(sample_file))
    assert "MarkItDown" in res_md
    print(" [PASS] convert_document(README.md)")

    # 3. Test analyze_document_metrics
    metrics_json = analyze_document_metrics(str(sample_file))
    metrics = json.loads(metrics_json)
    assert "word_count" in metrics and metrics["word_count"] > 0
    assert "estimated_llm_tokens" in metrics
    print(f" [PASS] analyze_document_metrics() -> {metrics['word_count']} words, ~{metrics['estimated_llm_tokens']} tokens")

    # 4. Test error handling for non-existent file
    error_res = convert_document("non_existent_file.pdf")
    assert "Error" in error_res or "not exist" in error_res
    print(" [PASS] Error handling on missing file")

    print("\n🎉 ALL MCP TOOL TESTS PASSED!")

if __name__ == "__main__":
    test_mcp_tools()
