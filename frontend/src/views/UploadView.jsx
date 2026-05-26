import { useState, useRef } from 'react';
import { uploadResume } from '../services/api.js';

/**
 * UploadView — default landing page.
 * Supports drag-and-drop, file browse, and form submission.
 * On success dispatches SET_READY and auto-navigates to Analysis.
 */
export default function UploadView({ dispatch }) {
  const [file, setFile] = useState(null);
  const [fileInfo, setFileInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);
  const [jdDragging, setJdDragging] = useState(false);
  const [isJdExpanded, setIsJdExpanded] = useState(false);

  const [jdText, setJdText] = useState('');
  const [jdFile, setJdFile] = useState(null);

  const fileInputRef = useRef(null);
  const jdFileInputRef = useRef(null);

  // ── File selection ────────────────────────────────────────────────────────

  function handleFileSelect(selectedFile) {
    if (!selectedFile) return;
    setFile(selectedFile);
    setFileInfo(`Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(2)} KB)`);
    setError('');
  }

  // ── Drag & Drop ───────────────────────────────────────────────────────────

  function onDragOver(e) {
    e.preventDefault();
    setDragging(true);
  }

  function onDragLeave() {
    setDragging(false);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFileSelect(dropped);
  }

  // ── JD Drag & Drop ────────────────────────────────────────────────────────

  function onJdDragOver(e) {
    e.preventDefault();
    setJdDragging(true);
  }

  function onJdDragLeave() {
    setJdDragging(false);
  }

  function onJdDrop(e) {
    e.preventDefault();
    setJdDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setJdFile(dropped);
  }

  // ── Submission ────────────────────────────────────────────────────────────

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;

    setError('');
    setLoading(true);
    dispatch({ type: 'SET_PROCESSING', payload: { filename: file.name } });

    try {
      const result = await uploadResume(file, jdText, jdFile);

      dispatch({
        type: 'SET_READY',
        payload: result.data,
      });

    } catch (err) {
      setError(err.message || 'Failed to upload file. Please try again.');
      dispatch({ type: 'RESET' });
    } finally {
      setLoading(false);
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="upload-container">
      <div className="upload-wrapper">
        <h1 className="hero-title">
          <span className="title-heavy">RESUME</span>
          <span className="title-italic">Analyzer</span>
        </h1>
        <p className="hero-subtitle">INTELLIGENT PARSING &amp; PROFESSIONAL INSIGHTS</p>

        <form id="uploadForm" onSubmit={handleSubmit} encType="multipart/form-data">
          {/* Drop Zone */}
          <div
            id="uploadArea"
            className={`upload-area${dragging ? ' dragover' : ''}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => !loading && fileInputRef.current?.click()}
          >
            <div className="upload-icon">📄</div>
            <label htmlFor="fileInput" className="upload-label">
              Drop your resume here or{' '}
              <span className="link-text">browse files</span>
            </label>
            <input
              ref={fileInputRef}
              type="file"
              id="fileInput"
              name="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt,.md"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              required
            />
            {fileInfo && (
              <div className="file-info">{fileInfo}</div>
            )}
          </div>

          {/* Job Description (Optional) */}
          <div className="jd-section" style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '10px', textAlign: 'left' }}>
            <div
              className="upload-area"
              onClick={() => setIsJdExpanded(!isJdExpanded)}
              style={{
                padding: '1rem 1.5rem',
                marginBottom: '0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer'
              }}
            >
              <span style={{ fontSize: '0.95rem', fontWeight: '500', color: 'var(--text-secondary)' }}>
                Job Description (Optional)
              </span>
              <span
                className="accordion-icon"
                style={{
                  transform: isJdExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
                }}
              >
                ▼
              </span>
            </div>

            {isJdExpanded && (
              <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <textarea
                  placeholder="Paste job description text here..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    resize: 'vertical',
                    fontFamily: 'inherit'
                  }}
                />

                <div style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>OR</div>

                <div
                  className={`upload-area${jdDragging ? ' dragover' : ''}`}
                  onDragOver={onJdDragOver}
                  onDragLeave={onJdDragLeave}
                  onDrop={onJdDrop}
                  onClick={() => jdFileInputRef.current?.click()}
                  style={{ padding: '20px', minHeight: '120px', cursor: 'pointer' }}
                >
                  <div className="upload-icon" style={{ fontSize: '24px', marginBottom: '10px' }}>📄</div>
                  <label className="upload-label" style={{ fontSize: '0.9rem', cursor: 'pointer' }}>
                    Drop JD file here or{' '}
                    <span className="link-text">browse files</span>
                  </label>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
                    Supported: .txt, .md
                  </div>
                  <input
                    ref={jdFileInputRef}
                    type="file"
                    accept=".txt,.md"
                    style={{ display: 'none' }}
                    onChange={(e) => setJdFile(e.target.files[0])}
                  />
                  {jdFile && (
                    <div className="file-info" style={{ marginTop: '12px' }}>
                      Selected JD: {jdFile.name}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            id="submitBtn"
            className="btn-primary"
            disabled={loading}
            style={{ width: 'fit-content', margin: '20px auto 0', display: 'flex', justifyContent: 'center' }}
          >
            <span className="btn-text">
              {loading ? 'PROCESSING...' : 'ANALYZE RESUME'}
            </span>
          </button>
        </form>

        {/* Loading */}
        {loading && (
          <div className="loading show">
            <div className="spinner" />
            <p className="loading-text">PROCESSING DOCUMENT...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-box show">{error}</div>
        )}
      </div>
    </div>
  );
}
