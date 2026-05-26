import { useState, useRef, useCallback, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  enhanceResume,
  fetchTexContent,
  triggerPdfDownload,
  downloadTexBlob,
  compileRawLatex,
} from '../services/api.js';

/**
 * VisualEditor MVP — simple form fields mapped to resume state.
 */
function VisualEditorMVP({ data, onChange, disabled }) {
  const inputStyle = { 
    width: '100%', padding: '0.75rem', marginBottom: '0.75rem', 
    border: '1px solid var(--border-color)', borderRadius: '6px', 
    fontFamily: 'inherit', background: 'var(--surface-light)', color: 'var(--text-primary)' 
  };
  const textareaStyle = { ...inputStyle, resize: 'vertical', minHeight: '100px' };

  const handleChange = (section, field, value, index = null) => {
    const newData = JSON.parse(JSON.stringify(data)); // deep copy
    
    if (index !== null) {
      if (field === 'bullets') {
        newData[section][index][field] = value.split('\n');
      } else {
        newData[section][index][field] = value;
      }
    } else if (field) {
      if (!newData[section]) newData[section] = {};
      newData[section][field] = value;
    } else {
      newData[section] = value;
    }
    
    onChange(newData);
  };

  if (!data) return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>No structured data available</div>;

  return (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', opacity: disabled ? 0.4 : 1, pointerEvents: disabled ? 'none' : 'auto', height: '100%', overflowY: 'auto' }}>
      
      {/* Identity */}
      <div className="section-card" style={{ marginBottom: 0 }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Identity</h3>
        
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.75rem' }}>
          <label style={{ width: '90px', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>Name:</label>
          <input style={{...inputStyle, marginBottom: 0}} value={data.identity?.name || ''} onChange={e => handleChange('identity', 'name', e.target.value)} />
        </div>

        <div style={{ display: 'flex', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', flex: 3 }}>
            <label style={{ width: '90px', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>Email:</label>
            <input style={{...inputStyle, marginBottom: 0}} value={data.identity?.email || ''} onChange={e => handleChange('identity', 'email', e.target.value)} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', flex: 2 }}>
            <label style={{ marginRight: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500, whiteSpace: 'nowrap' }}>Phone No.:</label>
            <input style={{...inputStyle, marginBottom: 0}} value={data.identity?.phone || ''} onChange={e => handleChange('identity', 'phone', e.target.value)} />
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="section-card" style={{ marginBottom: 0 }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Professional Summary</h3>
        <textarea style={textareaStyle} value={data.analysis?.professional_summary || ''} onChange={e => handleChange('analysis', 'professional_summary', e.target.value)} placeholder="Summary..." />
      </div>

      {/* Experience */}
      {data.experience?.length > 0 && (
        <div className="section-card" style={{ marginBottom: 0 }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Experience</h3>
          {data.experience.map((exp, i) => (
            <div key={i} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: i < data.experience.length - 1 ? '1px solid var(--border-color)' : 'none' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <input style={inputStyle} value={exp.title || ''} onChange={e => handleChange('experience', 'title', e.target.value, i)} placeholder="Job Title" />
                </div>
                <div style={{ flex: 1 }}>
                  <input style={inputStyle} value={exp.company || ''} onChange={e => handleChange('experience', 'company', e.target.value, i)} placeholder="Company" />
                </div>
              </div>
              <textarea style={textareaStyle} value={(exp.bullets || []).join('\n')} onChange={e => handleChange('experience', 'bullets', e.target.value, i)} placeholder="Bullets (one per line)" />
            </div>
          ))}
        </div>
      )}

      {/* Projects */}
      {data.projects?.length > 0 && (
        <div className="section-card" style={{ marginBottom: 0 }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Projects</h3>
          {data.projects.map((proj, i) => (
            <div key={i} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: i < data.projects.length - 1 ? '1px solid var(--border-color)' : 'none' }}>
              <input style={inputStyle} value={proj.title || ''} onChange={e => handleChange('projects', 'title', e.target.value, i)} placeholder="Project Title" />
              <textarea style={textareaStyle} value={(proj.bullets || []).join('\n')} onChange={e => handleChange('projects', 'bullets', e.target.value, i)} placeholder="Bullets (one per line)" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * EditorView — split-panel LaTeX editor & Visual editor.
 */
export default function EditorView({ resume, analysis, editor, dispatch }) {
  const [viewMode, setViewMode]     = useState('split');
  const [loading, setLoading]       = useState(false);
  const [status, setStatus]         = useState('Ready');
  const [lineCount, setLineCount]   = useState(0);
  const [charCount, setCharCount]   = useState(0);
  
  // Dual-pane sync states
  const [latexDirty, setLatexDirty] = useState(false);
  const [visualDirty, setVisualDirty] = useState(false);
  const [visualData, setVisualData] = useState(null);
  
  const [showConfirm, setShowConfirm] = useState(false);

  const originalCodeRef             = useRef('');
  const monacoRef                   = useRef(null);

  // Initialize visual data when resume arrives
  useEffect(() => {
    if (resume && !visualDirty) {
      // Merge analysis summary into resume for seamless editing
      const initialData = JSON.parse(JSON.stringify(resume));
      if (!initialData.analysis) initialData.analysis = {};
      initialData.analysis.professional_summary = initialData.analysis.professional_summary || analysis?.professionalSummary || '';
      setVisualData(initialData);
    }
  }, [resume, analysis, visualDirty]);

  function handleEditorDidMount(editorInstance) {
    monacoRef.current = editorInstance;
    if (editor.latexCode) {
      updateStats(editor.latexCode);
    }
  }

  function handleLatexChange(value) {
    updateStats(value ?? '');
    dispatch({
      type: 'SET_EDITOR',
      payload: { latexCode: value ?? '', hasUnsavedChanges: true },
    });
    setLatexDirty(true);
    setStatus('LaTeX Modified');
  }

  function handleVisualChange(newData) {
    setVisualData(newData);
    setVisualDirty(true);
    setStatus('Text Modified');
  }

  function updateStats(code) {
    setLineCount(code.split('\n').length);
    setCharCount(code.length);
  }

  // ── Compile ─────────────────────────────────────────────────────────────

  const handleCompile = useCallback(async () => {
    if (loading) return;

    setLoading(true);
    setStatus('Compiling...');

    try {
      if (visualDirty) {
        // Run full LLM generation & rendering from updated JSON
        const result = await enhanceResume(visualData);

        dispatch({
          type: 'SET_EDITOR',
          payload: {
            fileId:           result.file_id,
            downloadBasename: result.download_basename ?? 'candidate_resume_ai_pack',
            isPdfAvailable:   result.pdf_available,
          },
        });

        const latexCode = await fetchTexContent(result.file_id, result.tex_filename ?? `${result.download_basename}.tex`);
        originalCodeRef.current = latexCode;

        dispatch({
          type: 'SET_EDITOR',
          payload: { latexCode, hasUnsavedChanges: false },
        });

        updateStats(latexCode);
      } 
      else if (latexDirty && editor.latexCode) {
        // Compile raw LaTeX directly without running LLM
        const result = await compileRawLatex(editor.latexCode);

        dispatch({
          type: 'SET_EDITOR',
          payload: {
            fileId:           result.file_id,
            downloadBasename: result.download_basename ?? 'candidate_resume_ai_pack',
            isPdfAvailable:   result.pdf_available,
            hasUnsavedChanges: false
          },
        });
      }

      // Reset both dirty states after successful compile
      setLatexDirty(false);
      setVisualDirty(false);
      setStatus('Ready to edit');

    } catch (err) {
      console.error(err);
      setStatus('Error — ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [loading, visualDirty, latexDirty, visualData, editor.latexCode, dispatch]);

  function handleReset() {
    setShowConfirm(true);
  }

  function confirmReset() {
    const original = originalCodeRef.current;
    dispatch({ type: 'SET_EDITOR', payload: { latexCode: original, hasUnsavedChanges: false } });
    monacoRef.current?.setValue(original);
    setLatexDirty(false);
    setStatus('Reset to original');
    setShowConfirm(false);
  }

  function cancelReset() {
    setShowConfirm(false);
  }

  function handleDownloadPdf() {
    if (!editor.fileId) return;
    const basename = editor.downloadBasename || 'candidate_resume_ai_pack';
    triggerPdfDownload(editor.fileId, `${basename}.pdf`);
  }

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

        <div className="editor-view-switch" role="tablist">
          {[
            { id: 'split',   label: 'SPLIT VIEW'    },
            { id: 'latex',   label: 'LATEX ONLY'    },
            { id: 'preview', label: 'PREVIEW ONLY'  },
          ].map(({ id, label }) => (
            <button
              key={id}
              className={`view-toggle-btn${viewMode === id ? ' active' : ''}`}
              onClick={() => setViewMode(id)}
            >
              {label}
            </button>
          ))}
        </div>

        <button
          className="toolbar-btn"
          id="compileBtn"
          onClick={handleCompile}
          disabled={loading || (!resume && !editor.latexCode) || (!latexDirty && !visualDirty)}
          style={latexDirty || visualDirty ? { background: 'var(--accent-primary)', color: 'white', display: 'inline-flex', alignItems: 'center' } : { display: 'inline-flex', alignItems: 'center' }}
        >
          {loading ? (
            <>
              <svg style={{ marginRight: '6px', animation: 'spin 1.2s linear infinite' }} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.2)" />
                <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
              </svg>
              COMPILING...
            </>
          ) : (
            <>
              <svg style={{ marginRight: '6px' }} width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
              COMPILE
            </>
          )}
        </button>

        {editor.latexCode && (
          <button className="toolbar-btn" id="resetBtn" onClick={handleReset} style={{ display: 'inline-flex', alignItems: 'center' }}>
            <svg style={{ marginRight: '6px' }} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <polyline points="3 3 3 8 8 8" />
            </svg>
            RESET
          </button>
        )}

        {editor.isPdfAvailable && editor.fileId && (
          <button
            className="toolbar-btn btn-download-pdf"
            id="downloadPdfBtn"
            onClick={handleDownloadPdf}
            style={{ background: 'var(--accent-secondary)', color: 'white', borderColor: 'var(--accent-secondary)', display: 'inline-flex', alignItems: 'center' }}
          >
            <svg style={{ marginRight: '6px' }} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            DOWNLOAD PDF
          </button>
        )}

        <span className="toolbar-status">
          <span className="status-label">STATUS:</span>
          <span className="status-text">{status}</span>
        </span>

        <div className="editor-info">
          <span className="info-label">LINES:</span>
          <span className="info-value">{lineCount}</span>
        </div>
      </div>

      {/* Editor workspace */}
      <div className={workspaceClass} id="editorWorkspace">
        
        {/* Custom Reset Confirmation Modal */}
        {showConfirm && (
          <div style={{ position: 'fixed', inset: 0, zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0, 0, 0, 0.4)', backdropFilter: 'blur(2px)' }}>
            <div style={{ background: 'var(--surface-white)', padding: '2rem', borderRadius: '12px', boxShadow: 'var(--shadow-xl)', maxWidth: '400px', width: '90%', border: '1px solid var(--border-color)' }}>
              <h3 style={{ marginBottom: '0.75rem', color: 'var(--text-primary)', fontSize: '1.25rem' }}>Reset Editor</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.5 }}>Are you sure you want to discard all your edits and revert to the original code? This cannot be undone.</p>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                <button className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', width: 'fit-content' }} onClick={cancelReset}>Cancel</button>
                <button className="btn-primary" style={{ background: 'var(--accent-primary)', color: 'white', borderColor: 'var(--accent-primary)', padding: '0.5rem 1rem', fontSize: '0.9rem', width: 'fit-content' }} onClick={confirmReset}>Yes, Reset</button>
              </div>
            </div>
          </div>
        )}

        {/* LaTeX Panel */}
        <section className="editor-panel latex-panel editor-island" style={{ position: 'relative' }}>
          
          {/* Lock Overlay for LaTeX when Visual is Dirty */}
          {visualDirty && (
            <div style={{ position: 'absolute', inset: 0, background: 'var(--overlay-dark-bg)', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
              <div style={{ background: 'var(--surface-white)', padding: '2rem', borderRadius: '12px', textAlign: 'center', border: '2px solid var(--accent-secondary)', boxShadow: 'var(--shadow-lg)' }}>
                <h3 style={{ color: 'var(--accent-secondary)', marginBottom: '0.5rem' }}>Text Changes Detected</h3>
                <p style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Press Compile to sync text edits to LaTeX.</p>
                <button className="btn-primary" onClick={handleCompile}>⚡ Compile & Sync</button>
              </div>
            </div>
          )}

          <div className="panel-header">
            <div>
              <div className="panel-eyebrow">SOURCE OF TRUTH</div>
              <h3 className="panel-title">Raw LaTeX Editor</h3>
            </div>
          </div>

          <div className="monaco-container" style={{ flex: 1, minHeight: 0 }}>
            {editor.latexCode ? (
              <Editor
                height="100%"
                defaultLanguage="latex"
                value={editor.latexCode}
                onChange={handleLatexChange}
                onMount={handleEditorDidMount}
                theme="vs-dark"
                options={{
                  fontSize: 14,
                  fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
                  minimap: { enabled: false },
                  wordWrap: 'off',
                  padding: { top: 16, bottom: 16 },
                }}
              />
            ) : (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(237,242,232,0.4)', fontFamily: 'var(--font-mono)' }}>
                Upload a resume to generate LaTeX
              </div>
            )}
          </div>
        </section>

        {/* Visual Panel */}
        <aside className="editor-panel visual-panel editor-island" style={{ position: 'relative' }}>
          
          {/* Lock Overlay for Visual when LaTeX is Dirty */}
          {latexDirty && (
            <div style={{ position: 'absolute', inset: 0, background: 'var(--overlay-light-bg)', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
              <div style={{ background: 'var(--surface-white)', padding: '2rem', borderRadius: '12px', textAlign: 'center', border: '2px solid var(--accent-primary)', boxShadow: 'var(--shadow-lg)' }}>
                <h3 style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem' }}>LaTeX Changes Detected</h3>
                <p style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Press Compile to sync LaTeX edits to the PDF.</p>
                <button className="btn-primary" onClick={handleCompile}>⚡ Compile & Sync</button>
              </div>
            </div>
          )}

          <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div className="panel-eyebrow">MVP PREVIEW</div>
              <h3 className="panel-title">Visual Text Editor</h3>
            </div>
            {editor.isPdfAvailable && !latexDirty && !visualDirty && (
              <button className="btn-secondary" onClick={handleDownloadPdf} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                Preview PDF
              </button>
            )}
          </div>

          <div style={{ flex: 1, minHeight: 0, background: 'var(--bg-canvas)' }}>
            <VisualEditorMVP 
              data={visualData} 
              onChange={handleVisualChange} 
              disabled={latexDirty} 
            />
          </div>
        </aside>

      </div>
    </div>
  );
}
