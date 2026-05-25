import { useState, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import {
  enhanceResume,
  fetchTexContent,
  triggerPdfDownload,
  downloadTexBlob,
} from '../services/api.js';

/**
 * EditorView — split-panel LaTeX editor.
 *
 * Left panel:  Monaco Editor (dark olive theme)
 * Right panel: Visual placeholder (matches original styles)
 * Top toolbar: view-mode toggles, Reset, Download Edited, Compile button, status, stats
 */
export default function EditorView({ resume, analysis, editor, dispatch }) {
  const [viewMode, setViewMode]     = useState('split');   // 'split' | 'latex' | 'preview'
  const [loading, setLoading]       = useState(false);
  const [status, setStatus]         = useState('Ready');
  const [lineCount, setLineCount]   = useState(0);
  const [charCount, setCharCount]   = useState(0);
  const originalCodeRef             = useRef('');
  const monacoRef                   = useRef(null);

  // ── Monaco ready ─────────────────────────────────────────────────────────

  function handleEditorDidMount(editorInstance) {
    monacoRef.current = editorInstance;
    if (editor.latexCode) {
      updateStats(editor.latexCode);
    }
  }

  function handleEditorChange(value) {
    updateStats(value ?? '');
    dispatch({
      type: 'SET_EDITOR',
      payload: { latexCode: value ?? '', hasUnsavedChanges: true },
    });
    setStatus('Modified');
  }

  function updateStats(code) {
    setLineCount(code.split('\n').length);
    setCharCount(code.length);
  }

  // ── Compile (enhance) ─────────────────────────────────────────────────────

  const handleCompile = useCallback(async () => {
    if (!resume || loading) return;

    setLoading(true);
    setStatus('Generating LaTeX...');

    try {
      const payload = {
        ...resume,
        analysis: {
          professional_summary: analysis?.professionalSummary ?? ''
        }
      };
      const result = await enhanceResume(payload);

      dispatch({
        type: 'SET_EDITOR',
        payload: {
          fileId:           result.file_id,
          downloadBasename: result.download_basename ?? 'candidate_resume_ai_pack',
          isPdfAvailable:   result.pdf_available,
        },
      });

      // Fetch .tex content
      const latexCode = await fetchTexContent(
        result.file_id,
        result.tex_filename ?? `${result.download_basename}.tex`,
      );

      originalCodeRef.current = latexCode;

      dispatch({
        type: 'SET_EDITOR',
        payload: { latexCode, hasUnsavedChanges: false },
      });

      updateStats(latexCode);
      setStatus('Ready to edit');

    } catch (err) {
      console.error(err);
      setStatus('Error — ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [resume, loading, dispatch]);

  // ── Reset ─────────────────────────────────────────────────────────────────

  function handleReset() {
    if (!window.confirm('Reset to original generated code?')) return;
    const original = originalCodeRef.current;
    dispatch({ type: 'SET_EDITOR', payload: { latexCode: original, hasUnsavedChanges: false } });
    monacoRef.current?.setValue(original);
    setStatus('Reset to original');
  }

  // ── Download edited ────────────────────────────────────────────────────────

  function handleDownloadEdited() {
    const basename = editor.downloadBasename || 'candidate_resume_ai_pack';
    downloadTexBlob(editor.latexCode, `${basename}_edited.tex`);
    setStatus('Downloaded');
    setTimeout(() => setStatus('Ready to edit'), 2000);
  }

  // ── Download PDF ───────────────────────────────────────────────────────────

  function handleDownloadPdf() {
    if (!editor.fileId) return;
    const basename = editor.downloadBasename || 'candidate_resume_ai_pack';
    triggerPdfDownload(editor.fileId, `${basename}.pdf`);
  }

  // ── Render ────────────────────────────────────────────────────────────────

  const workspaceClass = `editor-workspace ${
    viewMode === 'split'   ? 'split-view'   :
    viewMode === 'latex'   ? 'latex-only'   :
    'preview-only'
  }`;

  return (
    <div className="editor-view">
      {/* Toolbar */}
      <div className="editor-toolbar">
        <div className="editor-top-title">
          <span className="top-title-heavy">Hybrid</span>
          <span className="top-title-italic">Editor</span>
        </div>

        {/* View mode toggle */}
        <div className="editor-view-switch" role="tablist" aria-label="Editor view selector">
          {[
            { id: 'split',   label: 'SPLIT VIEW'    },
            { id: 'latex',   label: 'LATEX ONLY'    },
            { id: 'preview', label: 'PREVIEW ONLY'  },
          ].map(({ id, label }) => (
            <button
              key={id}
              className={`view-toggle-btn${viewMode === id ? ' active' : ''}`}
              onClick={() => setViewMode(id)}
              aria-pressed={viewMode === id}
              id={`show${id.charAt(0).toUpperCase() + id.slice(1)}ViewBtn`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Compile */}
        <button
          className="toolbar-btn"
          id="compileBtn"
          onClick={handleCompile}
          disabled={loading || !resume}
          title={!resume ? 'Upload a resume first' : 'Generate LaTeX from resume'}
        >
          {loading ? '⏳ GENERATING...' : '⚡ COMPILE'}
        </button>

        {/* Reset */}
        {editor.latexCode && (
          <button className="toolbar-btn" id="resetBtn" onClick={handleReset}>
            ↺ RESET
          </button>
        )}

        {/* Download edited */}
        {editor.latexCode && (
          <button className="toolbar-btn" id="downloadEditedBtn" onClick={handleDownloadEdited}>
            ↓ DOWNLOAD EDITED
          </button>
        )}

        {/* Download PDF */}
        {editor.isPdfAvailable && editor.fileId && (
          <button
            className="toolbar-btn btn-download-pdf"
            id="downloadPdfBtn"
            onClick={handleDownloadPdf}
            style={{ background: 'var(--accent-secondary)', color: 'white', borderColor: 'var(--accent-secondary)' }}
          >
            ↓ DOWNLOAD PDF
          </button>
        )}

        {/* Status + stats */}
        <span className="toolbar-status">
          <span className="status-label">STATUS:</span>
          <span className="status-text" id="editorStatus">{status}</span>
        </span>

        <div className="editor-info">
          <span className="info-label">LINES:</span>
          <span className="info-value" id="lineCount">{lineCount}</span>
          <span className="info-separator">|</span>
          <span className="info-label">CHARS:</span>
          <span className="info-value" id="charCount">{charCount}</span>
        </div>
      </div>

      {/* Editor workspace */}
      <div className={workspaceClass} id="editorWorkspace">
        {/* LaTeX Panel */}
        <section
          className="editor-panel latex-panel editor-island"
          aria-labelledby="latexPanelTitle"
        >
          <div className="panel-header">
            <div>
              <div className="panel-eyebrow">SOURCE OF TRUTH</div>
              <h3 className="panel-title" id="latexPanelTitle">Raw LaTeX Editor</h3>
            </div>
            <p className="panel-copy">Full control over formatting, structure, and content.</p>
          </div>

          <div className="monaco-container" style={{ flex: 1, minHeight: 0 }}>
            {editor.latexCode ? (
              <Editor
                height="100%"
                defaultLanguage="latex"
                value={editor.latexCode}
                onChange={handleEditorChange}
                onMount={handleEditorDidMount}
                theme="vs-dark"
                options={{
                  fontSize: 14,
                  fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
                  lineHeight: 1.6,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'off',
                  renderLineHighlight: 'all',
                  padding: { top: 16, bottom: 16 },
                  scrollbar: { verticalScrollbarSize: 8 },
                }}
              />
            ) : (
              <div style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'rgba(237,242,232,0.4)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem',
                letterSpacing: '0.08em',
                padding: '2rem',
                textAlign: 'center',
              }}>
                {resume
                  ? 'Click ⚡ COMPILE to generate LaTeX'
                  : 'Upload a resume first'}
              </div>
            )}
          </div>
        </section>

        {/* Visual Panel */}
        <aside
          className="editor-panel visual-panel editor-island"
          id="visualEditorPanel"
          aria-labelledby="visualPanelTitle"
        >
          <div className="panel-header">
            <div>
              <div className="panel-eyebrow">PHASE 1 PLACEHOLDER</div>
              <h3 className="panel-title" id="visualPanelTitle">Visual Editor Preview</h3>
            </div>
            <p className="panel-copy">
              This checkpoint reserves the visual editing surface without
              changing compile or render behavior.
            </p>
          </div>
          <div className="visual-placeholder" id="visualPlaceholder">
            <div className="visual-placeholder-card">
              <span className="placeholder-badge">Upcoming</span>
              <h4>Content-only editing lands in the next checkpoints</h4>
              <p>
                Titles, summaries, bullets, and skills will become editable here
                after we add safe LaTeX-to-node mapping.
              </p>
            </div>
            <div className="visual-placeholder-list" aria-hidden="true">
              <div className="placeholder-line placeholder-line-lg" />
              <div className="placeholder-line placeholder-line-md" />
              <div className="placeholder-line placeholder-line-sm" />
              <div className="placeholder-block">
                <div className="placeholder-line placeholder-line-lg" />
                <div className="placeholder-line placeholder-line-md" />
                <div className="placeholder-line placeholder-line-md" />
              </div>
              <div className="placeholder-block">
                <div className="placeholder-line placeholder-line-lg" />
                <div className="placeholder-line placeholder-line-sm" />
                <div className="placeholder-line placeholder-line-md" />
              </div>
            </div>
            <p className="visual-placeholder-note">
              Layout edits remain intentionally locked to the LaTeX editor.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
