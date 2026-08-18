/**
 * MarkItDown Studio - Client Application Logic
 * Handles file uploads, URL conversions, batch processing, markdown rendering,
 * metrics calculation, and user settings.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global State
  const state = {
    currentResult: null,
    batchQueue: [],
    history: JSON.parse(localStorage.getItem('markitdown_history') || '[]'),
    settings: JSON.parse(localStorage.getItem('markitdown_settings') || JSON.stringify({
      llm_api_key: '',
      llm_base_url: 'https://openrouter.ai/api/v1',
      llm_model: 'openai/gpt-4o-mini',
      llm_prompt: '',
      cu_endpoint: '',
      cu_analyzer_id: '',
      docintel_endpoint: '',
      enable_plugins: true,
      theme: 'dark'
    })),
    currentViewMode: 'split' // 'split' | 'rendered' | 'raw'
  };

  // DOM Elements
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const batchFileInput = document.getElementById('batch-file-input');
  const urlInput = document.getElementById('url-input');
  const btnConvertUrl = document.getElementById('btn-convert-url');
  
  const loadingIndicator = document.getElementById('loading-indicator');
  const loadingText = document.getElementById('loading-text');
  const resultsWrapper = document.getElementById('results-wrapper');
  
  const renderedContent = document.getElementById('rendered-content');
  const rawTextarea = document.getElementById('raw-markdown-textarea');
  const previewPanes = document.getElementById('preview-panes');
  
  // Stat elements
  const statDocName = document.getElementById('stat-doc-name');
  const statWords = document.getElementById('stat-words');
  const statChars = document.getElementById('stat-chars');
  const statTokens = document.getElementById('stat-tokens');
  const statTime = document.getElementById('stat-time');
  const statSize = document.getElementById('stat-size');

  // Action Buttons
  const btnCopy = document.getElementById('btn-copy-md');
  const btnDownloadMd = document.getElementById('btn-download-md');
  const btnDownloadHtml = document.getElementById('btn-download-html');
  const btnSettings = document.getElementById('btn-settings');
  const btnHistory = document.getElementById('btn-history');
  const btnFormats = document.getElementById('btn-formats');
  const btnThemeToggle = document.getElementById('btn-theme-toggle');

  // Modals
  const settingsModal = document.getElementById('settings-modal');
  const historyModal = document.getElementById('history-modal');
  const formatsModal = document.getElementById('formats-modal');
  const btnSaveSettings = document.getElementById('btn-save-settings');

  // Initialize
  initTheme();
  setupNavigationTabs();
  setupDropzone();
  setupViewModeToggles();
  setupActions();
  setupModals();
  renderHistory();

  /* ==========================================================================
     Theme Management
     ========================================================================== */
  function initTheme() {
    document.documentElement.setAttribute('data-theme', state.settings.theme || 'dark');
    updateThemeIcon();
  }

  btnThemeToggle.addEventListener('click', () => {
    const nextTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    state.settings.theme = nextTheme;
    saveSettings();
    updateThemeIcon();
  });

  function updateThemeIcon() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btnThemeToggle.innerHTML = isDark 
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
  }

  /* ==========================================================================
     Navigation Tabs
     ========================================================================== */
  function setupNavigationTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const tabTarget = btn.getAttribute('data-tab');
        document.querySelectorAll('.panel-content').forEach(p => p.classList.remove('active'));
        const targetPanel = document.getElementById(tabTarget);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }
      });
    });
  }

  /* ==========================================================================
     Dropzone & File Uploads
     ========================================================================== */
  function setupDropzone() {
    if (!dropzone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('drag-active');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('drag-active');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        if (files.length === 1) {
          handleSingleFileUpload(files[0]);
        } else {
          // Switch to batch tab and handle multiple
          switchToBatchTab(files);
        }
      }
    });

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleSingleFileUpload(e.target.files[0]);
      }
    });

    // Sample Quick Loaders
    document.querySelectorAll('.sample-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const sampleType = link.getAttribute('data-sample');
        loadSampleData(sampleType);
      });
    });

    // Batch upload listeners
    const batchDropzone = document.getElementById('batch-dropzone');
    if (batchDropzone) {
      batchDropzone.addEventListener('click', () => batchFileInput.click());
      batchFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
          addFilesToBatch(Array.from(e.target.files));
        }
      });
    }

    // Convert URL button
    btnConvertUrl.addEventListener('click', handleUrlConversion);
    urlInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleUrlConversion();
    });
  }

  function showLoading(msg = 'Converting document...') {
    loadingText.textContent = msg;
    loadingIndicator.style.display = 'block';
    resultsWrapper.style.display = 'none';
  }

  function hideLoading() {
    loadingIndicator.style.display = 'none';
  }

  /* ==========================================================================
     Single File Conversion
     ========================================================================== */
  async function handleSingleFileUpload(file) {
    showLoading(`Converting "${file.name}" with MarkItDown...`);
    const formData = new FormData();
    formData.append('file', file);

    // Append configured AI / Azure options
    if (state.settings.llm_api_key) formData.append('llm_api_key', state.settings.llm_api_key);
    if (state.settings.llm_base_url) formData.append('llm_base_url', state.settings.llm_base_url);
    if (state.settings.llm_model) formData.append('llm_model', state.settings.llm_model);
    if (state.settings.llm_prompt) formData.append('llm_prompt', state.settings.llm_prompt);
    if (state.settings.cu_endpoint) formData.append('cu_endpoint', state.settings.cu_endpoint);
    if (state.settings.cu_analyzer_id) formData.append('cu_analyzer_id', state.settings.cu_analyzer_id);
    if (state.settings.docintel_endpoint) formData.append('docintel_endpoint', state.settings.docintel_endpoint);
    formData.append('enable_plugins', state.settings.enable_plugins);

    try {
      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Conversion failed' }));
        throw new Error(errorData.detail || 'Failed to convert file');
      }

      const result = await response.json();
      if (!result.success && result.error) {
        throw new Error(result.error);
      }

      displayConversionResult(result);
      addToHistory(result);
      showToast('Document converted successfully!', 'success');
    } catch (err) {
      console.error(err);
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      hideLoading();
    }
  }

  /* ==========================================================================
     URL Conversion
     ========================================================================== */
  async function handleUrlConversion() {
    const url = urlInput.value.trim();
    if (!url) {
      showToast('Please enter a valid URL', 'error');
      return;
    }

    showLoading(`Fetching and converting ${url}...`);

    try {
      const payload = {
        url,
        llm_api_key: state.settings.llm_api_key || null,
        llm_base_url: state.settings.llm_base_url || null,
        llm_model: state.settings.llm_model || null,
      };

      const response = await fetch('/api/convert-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'URL conversion failed' }));
        throw new Error(errorData.detail || 'URL conversion failed');
      }

      const result = await response.json();
      if (!result.success && result.error) {
        throw new Error(result.error);
      }

      displayConversionResult(result);
      addToHistory(result);
      showToast('URL converted successfully!', 'success');
    } catch (err) {
      console.error(err);
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      hideLoading();
    }
  }

  /* ==========================================================================
     Result Display & Live Markdown Rendering
     ========================================================================== */
  function displayConversionResult(result) {
    state.currentResult = result;
    const md = result.markdown || '';

    // Update stats
    statDocName.textContent = result.filename || 'Converted Document';
    statDocName.title = result.filename || '';
    
    if (result.stats) {
      statWords.textContent = Number(result.stats.word_count || 0).toLocaleString();
      statChars.textContent = Number(result.stats.char_count || 0).toLocaleString();
      statTokens.textContent = `~${Number(result.stats.estimated_tokens || 0).toLocaleString()}`;
      statTime.textContent = `${result.stats.duration_ms} ms`;
      
      const inKb = (result.stats.input_size_bytes / 1024).toFixed(1);
      const outKb = (result.stats.output_size_bytes / 1024).toFixed(1);
      statSize.textContent = `${inKb} KB → ${outKb} KB`;
    }

    // Render HTML preview using marked.js
    if (!md.trim()) {
      renderedContent.innerHTML = `
        <div style="text-align: center; padding: 3rem 1.5rem; color: var(--text-muted);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin: 0 auto 1rem; display: block; opacity: 0.5;">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">Documento sin contenido de texto</h3>
          <p style="font-size: 0.85rem; max-width: 480px; margin: 0 auto; line-height: 1.5;">
            Este archivo no contiene texto legible directamente o requiere Visión por IA (OCR). Si es una imagen o documento escaneado, puedes configurar tu clave de OpenAI en <strong>Configuración ⚙️</strong> para transcribirlo.
          </p>
        </div>
      `;
    } else if (typeof marked !== 'undefined') {
      marked.setOptions({
        gfm: true,
        breaks: true,
        headerIds: true,
      });
      renderedContent.innerHTML = marked.parse(md);
    } else {
      renderedContent.innerHTML = `<pre>${escapeHtml(md)}</pre>`;
    }

    // Syntax highlighting with highlight.js
    if (typeof hljs !== 'undefined' && md.trim()) {
      renderedContent.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
      });
    }

    // Populate Raw Textarea
    rawTextarea.value = md || '<!-- El documento no generó contenido de texto -->';

    // Show Results section
    resultsWrapper.style.display = 'block';
    resultsWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ==========================================================================
     View Mode Controls (Split / Rendered / Raw)
     ========================================================================== */
  function setupViewModeToggles() {
    const viewButtons = document.querySelectorAll('.view-toggle-btn');
    viewButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        viewButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const mode = btn.getAttribute('data-view');
        state.currentViewMode = mode;
        previewPanes.className = `preview-panes-container mode-${mode}`;
      });
    });
  }

  /* ==========================================================================
     Action Buttons (Copy, Download MD, Download HTML)
     ========================================================================== */
  function setupActions() {
    // Copy Markdown
    btnCopy.addEventListener('click', async () => {
      if (!state.currentResult || !state.currentResult.markdown) return;
      try {
        await navigator.clipboard.writeText(state.currentResult.markdown);
        showToast('Copied Markdown to clipboard!', 'success');
      } catch (err) {
        // Fallback copy
        rawTextarea.select();
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
      }
    });

    // Download .md
    btnDownloadMd.addEventListener('click', () => {
      if (!state.currentResult || !state.currentResult.markdown) return;
      const baseName = (state.currentResult.filename || 'document').replace(/\.[^/.]+$/, "");
      const fileName = `${baseName}.md`;
      downloadBlob(state.currentResult.markdown, fileName, 'text/markdown');
      showToast(`Downloaded ${fileName}`, 'success');
    });

    // Download HTML
    btnDownloadHtml.addEventListener('click', () => {
      if (!state.currentResult) return;
      const baseName = (state.currentResult.filename || 'document').replace(/\.[^/.]+$/, "");
      const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(state.currentResult.title || baseName)}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1e293b; }
    pre { background: #f1f5f9; padding: 16px; border-radius: 8px; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
    th { background: #f8fafc; }
  </style>
</head>
<body>
${renderedContent.innerHTML}
</body>
</html>`;
      downloadBlob(fullHtml, `${baseName}.html`, 'text/html');
      showToast(`Downloaded ${baseName}.html`, 'success');
    });
  }

  function downloadBlob(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /* ==========================================================================
     Batch Conversion Logic
     ========================================================================== */
  function switchToBatchTab(files) {
    const batchTabBtn = document.querySelector('[data-tab="panel-batch"]');
    if (batchTabBtn) batchTabBtn.click();
    addFilesToBatch(Array.from(files));
  }

  function addFilesToBatch(files) {
    files.forEach(file => {
      state.batchQueue.push({
        file,
        name: file.name,
        size: file.size,
        status: 'pending', // 'pending' | 'converting' | 'success' | 'error'
        result: null,
        error: null
      });
    });
    renderBatchTable();
  }

  const btnProcessBatch = document.getElementById('btn-process-batch');
  const btnDownloadZip = document.getElementById('btn-download-zip');
  const btnClearBatch = document.getElementById('btn-clear-batch');

  if (btnProcessBatch) {
    btnProcessBatch.addEventListener('click', processBatchQueue);
  }
  if (btnClearBatch) {
    btnClearBatch.addEventListener('click', () => {
      state.batchQueue = [];
      renderBatchTable();
    });
  }
  if (btnDownloadZip) {
    btnDownloadZip.addEventListener('click', downloadBatchZip);
  }

  function renderBatchTable() {
    const tbody = document.getElementById('batch-table-body');
    const batchControls = document.getElementById('batch-controls');
    if (!tbody) return;

    if (state.batchQueue.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">No files in queue. Drag & drop files above to get started.</td></tr>`;
      if (batchControls) batchControls.style.display = 'none';
      return;
    }

    if (batchControls) batchControls.style.display = 'flex';
    tbody.innerHTML = '';

    state.batchQueue.forEach((item, index) => {
      const tr = document.createElement('tr');
      
      let statusBadge = `<span class="batch-status-badge status-pending">Pending</span>`;
      if (item.status === 'converting') {
        statusBadge = `<span class="batch-status-badge status-converting">Converting...</span>`;
      } else if (item.status === 'success') {
        statusBadge = `<span class="batch-status-badge status-success">Done (${item.result.stats.duration_ms}ms)</span>`;
      } else if (item.status === 'error') {
        statusBadge = `<span class="batch-status-badge status-error">Error</span>`;
      }

      tr.innerHTML = `
        <td><strong>${escapeHtml(item.name)}</strong></td>
        <td>${(item.size / 1024).toFixed(1)} KB</td>
        <td>${statusBadge}</td>
        <td>${item.result ? `~${item.result.stats.estimated_tokens} tokens` : '-'}</td>
        <td>
          ${item.result ? `
            <button class="btn-secondary btn-sm preview-batch-item" data-index="${index}">View</button>
            <button class="btn-secondary btn-sm download-batch-item" data-index="${index}">.md</button>
          ` : `<button class="icon-button remove-batch-item" data-index="${index}">✕</button>`}
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Attach row events
    tbody.querySelectorAll('.preview-batch-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.getAttribute('data-index'));
        const item = state.batchQueue[idx];
        if (item && item.result) {
          displayConversionResult(item.result);
        }
      });
    });

    tbody.querySelectorAll('.download-batch-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.getAttribute('data-index'));
        const item = state.batchQueue[idx];
        if (item && item.result) {
          const baseName = item.name.replace(/\.[^/.]+$/, "");
          downloadBlob(item.result.markdown, `${baseName}.md`, 'text/markdown');
        }
      });
    });

    tbody.querySelectorAll('.remove-batch-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.getAttribute('data-index'));
        state.batchQueue.splice(idx, 1);
        renderBatchTable();
      });
    });

    // Check if zip download should be active
    const hasSuccess = state.batchQueue.some(i => i.status === 'success');
    if (btnDownloadZip) {
      btnDownloadZip.disabled = !hasSuccess;
      btnDownloadZip.style.opacity = hasSuccess ? '1' : '0.5';
    }
  }

  async function processBatchQueue() {
    const pendingItems = state.batchQueue.filter(i => i.status === 'pending');
    if (pendingItems.length === 0) {
      showToast('No pending files to process', 'error');
      return;
    }

    btnProcessBatch.disabled = true;
    for (const item of state.batchQueue) {
      if (item.status === 'pending') {
        item.status = 'converting';
        renderBatchTable();

        const formData = new FormData();
        formData.append('file', item.file);
        if (state.settings.llm_api_key) formData.append('llm_api_key', state.settings.llm_api_key);
        if (state.settings.llm_base_url) formData.append('llm_base_url', state.settings.llm_base_url);
        if (state.settings.llm_model) formData.append('llm_model', state.settings.llm_model);
        formData.append('enable_plugins', state.settings.enable_plugins);

        try {
          const res = await fetch('/api/convert', { method: 'POST', body: formData });
          const result = await res.json();
          if (result.success) {
            item.status = 'success';
            item.result = result;
            addToHistory(result);
          } else {
            item.status = 'error';
            item.error = result.error || 'Conversion error';
          }
        } catch (e) {
          item.status = 'error';
          item.error = e.message;
        }
        renderBatchTable();
      }
    }
    btnProcessBatch.disabled = false;
    showToast('Batch processing complete!', 'success');
  }

  async function downloadBatchZip() {
    if (typeof JSZip === 'undefined') {
      showToast('Zip library loading...', 'error');
      return;
    }

    const zip = new JSZip();
    let count = 0;

    state.batchQueue.forEach(item => {
      if (item.status === 'success' && item.result) {
        const baseName = item.name.replace(/\.[^/.]+$/, "");
        zip.file(`${baseName}.md`, item.result.markdown);
        count++;
      }
    });

    if (count === 0) {
      showToast('No successfully converted files to zip', 'error');
      return;
    }

    const content = await zip.generateAsync({ type: 'blob' });
    const zipUrl = URL.createObjectURL(content);
    const a = document.createElement('a');
    a.href = zipUrl;
    a.download = `markitdown_converted_${Date.now()}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(zipUrl);
    showToast(`Downloaded ZIP containing ${count} documents`, 'success');
  }

  /* ==========================================================================
     Sample Data Loader
     ========================================================================== */
  function loadSampleData(type) {
    let sampleMd = '';
    let name = 'sample_document.docx';

    if (type === 'report') {
      name = 'Quarterly_Financial_Report.xlsx';
      sampleMd = `# Quarterly Financial & Growth Report

## Executive Summary
This document summarizes corporate performance across key operational metrics for Q3 2026.

### Key Financial Highlights
- **Total Revenue**: $4,850,000 *(+18% YoY)*
- **Net Operating Margin**: 28.4%
- **R&D Allocation**: $850,000

| Division | Q2 2026 | Q3 2026 | Variance (%) |
| :--- | :--- | :--- | :--- |
| Cloud Services | $1,800,000 | $2,250,000 | +25.0% |
| Enterprise AI | $950,000 | $1,400,000 | +47.3% |
| Legacy Consulting | $1,450,000 | $1,200,000 | -17.2% |

> **Note**: Enterprise AI adoption exceeded quarterly forecasts by 35%, driven by automated document pipeline transformations.
`;
    } else if (type === 'code') {
      name = 'data_pipeline_spec.json';
      sampleMd = `# Data Pipeline Architecture Specification

This specification outlines the streaming ETL conversion workflow.

\`\`\`python
from markitdown import MarkItDown

# Universal converter initialization
md = MarkItDown(enable_plugins=True)
result = md.convert("annual_report.pdf")

print(f"Title: {result.title}")
print(result.markdown)
\`\`\`

### Conversion Flow
1. **Intake Stage**: Magika MIME detection and header verification.
2. **Converter Route**: Dispatch to PDF, DOCX, XLSX or Vision OCR processor.
3. **Structured Emission**: Output GitHub Flavored Markdown (GFM).
`;
    }

    const dummyResult = {
      success: true,
      filename: name,
      title: name.replace(/\.[^/.]+$/, ""),
      markdown: sampleMd,
      stats: {
        char_count: sampleMd.length,
        word_count: sampleMd.split(/\s+/).length,
        line_count: sampleMd.splitlines().length,
        estimated_tokens: Math.ceil(sampleMd.length / 4),
        duration_ms: 18.5,
        input_size_bytes: 48500,
        output_size_bytes: sampleMd.length
      }
    };

    displayConversionResult(dummyResult);
    addToHistory(dummyResult);
    showToast(`Loaded sample: ${name}`, 'success');
  }

  /* ==========================================================================
     Modals & Configuration Management
     ========================================================================== */
  function setupModals() {
    // Settings
    btnSettings.addEventListener('click', () => {
      document.getElementById('setting-llm-key').value = state.settings.llm_api_key || '';
      document.getElementById('setting-llm-base').value = state.settings.llm_base_url || '';
      document.getElementById('setting-llm-model').value = state.settings.llm_model || 'openai/gpt-4o-mini';
      document.getElementById('setting-llm-prompt').value = state.settings.llm_prompt || '';
      document.getElementById('setting-cu-endpoint').value = state.settings.cu_endpoint || '';
      document.getElementById('setting-cu-analyzer').value = state.settings.cu_analyzer_id || '';
      document.getElementById('setting-docintel-endpoint').value = state.settings.docintel_endpoint || '';
      document.getElementById('setting-enable-plugins').checked = state.settings.enable_plugins !== false;

      openModal(settingsModal);
    });

    btnSaveSettings.addEventListener('click', () => {
      state.settings.llm_api_key = document.getElementById('setting-llm-key').value.trim();
      state.settings.llm_base_url = document.getElementById('setting-llm-base').value.trim();
      state.settings.llm_model = document.getElementById('setting-llm-model').value.trim() || 'openai/gpt-4o-mini';
      state.settings.llm_prompt = document.getElementById('setting-llm-prompt').value.trim();
      state.settings.cu_endpoint = document.getElementById('setting-cu-endpoint').value.trim();
      state.settings.cu_analyzer_id = document.getElementById('setting-cu-analyzer').value.trim();
      state.settings.docintel_endpoint = document.getElementById('setting-docintel-endpoint').value.trim();
      state.settings.enable_plugins = document.getElementById('setting-enable-plugins').checked;

      saveSettings();
      closeModal(settingsModal);
      showToast('Settings saved!', 'success');
    });

    // History
    btnHistory.addEventListener('click', () => {
      renderHistory();
      openModal(historyModal);
    });

    // Formats
    btnFormats.addEventListener('click', () => openModal(formatsModal));

    // Close on click outside or close buttons
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal(overlay);
      });
    });

    document.querySelectorAll('.close-modal-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const modal = btn.closest('.modal-overlay');
        if (modal) closeModal(modal);
      });
    });
  }

  function openModal(modal) {
    if (modal) modal.classList.add('open');
  }

  function closeModal(modal) {
    if (modal) modal.classList.remove('open');
  }

  function saveSettings() {
    localStorage.setItem('markitdown_settings', JSON.stringify(state.settings));
  }

  /* ==========================================================================
     Session History
     ========================================================================== */
  function addToHistory(result) {
    if (!result || !result.markdown) return;
    const item = {
      id: Date.now(),
      filename: result.filename || 'Untitled',
      title: result.title || result.filename,
      markdown: result.markdown,
      stats: result.stats,
      date: new Date().toLocaleTimeString()
    };
    state.history.unshift(item);
    if (state.history.length > 20) state.history.pop();
    localStorage.setItem('markitdown_history', JSON.stringify(state.history));
  }

  function renderHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;

    if (state.history.length === 0) {
      list.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 2rem;">No recent conversions in this session.</p>`;
      return;
    }

    list.innerHTML = '';
    state.history.forEach(item => {
      const card = document.createElement('div');
      card.style.cssText = `
        background: var(--bg-surface-secondary);
        padding: 0.85rem 1rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        transition: all 0.2s ease;
      `;
      card.innerHTML = `
        <div>
          <strong style="font-size: 0.9rem;">${escapeHtml(item.filename)}</strong>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${item.date} • ${item.stats ? item.stats.word_count : 0} words • ~${item.stats ? item.stats.estimated_tokens : 0} tokens</div>
        </div>
        <button class="btn-secondary btn-sm">Load</button>
      `;
      card.addEventListener('click', () => {
        displayConversionResult(item);
        closeModal(historyModal);
        showToast(`Loaded ${item.filename}`, 'success');
      });
      list.appendChild(card);
    });
  }

  /* ==========================================================================
     Toasts & Utility Helpers
     ========================================================================== */
  function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success'
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;

    toast.innerHTML = `${icon}<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
