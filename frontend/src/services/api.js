// ─── API Service ──────────────────────────────────────────────────────────────
// All calls go through the Vite dev proxy to Flask on localhost:5000.
// In production, Flask must serve from the same origin or CORS must be configured.

const BASE_URL = '';   // proxy handles routing — no host prefix needed

/**
 * POST /upload  — multipart PDF/image upload
 * Returns { success, data, cached, input_type } from Flask
 */
export async function uploadResume(file, jdText, jdFile) {
  const formData = new FormData();
  formData.append('file', file);
  if (jdText && jdText.trim()) {
    formData.append('jd_text', jdText.trim());
  } else if (jdFile) {
    formData.append('jd_file', jdFile);
  }

  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  const json = await response.json();

  if (!response.ok || !json.success) {
    throw new Error(json.error ?? 'Upload failed');
  }

  return json;   // { success, data, cached, input_type }
}

/**
 * POST /enhance  — send resume_v2 JSON, get file_id + pdf_available
 * Returns { success, file_id, tex_filename, pdf_filename, download_basename, pdf_available, cached }
 */
export async function enhanceResume(resumeData) {
  const response = await fetch(`${BASE_URL}/enhance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume: resumeData }),
  });

  const json = await response.json();

  if (!response.ok || !json.success) {
    throw new Error(json.error ?? 'Enhancement failed');
  }

  return json;   // { success, file_id, tex_filename, pdf_filename, download_basename, pdf_available, cached }
}

/**
 * POST /compile-latex  — send raw LaTeX code, get file_id + pdf_available
 * Returns { success, file_id, tex_filename, pdf_filename, download_basename, pdf_available }
 */
export async function compileRawLatex(latexCode) {
  const response = await fetch(`${BASE_URL}/compile-latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex_code: latexCode }),
  });

  const json = await response.json();

  if (!response.ok || !json.success) {
    throw new Error(json.error ?? 'Compilation failed');
  }

  return json;
}

/**
 * GET /download-tex/:fileId  — fetch raw LaTeX content as text
 * Returns string (LaTeX source)
 */
export async function fetchTexContent(fileId, texFilename) {
  const url = `${BASE_URL}/download-tex/${fileId}?download_name=${encodeURIComponent(texFilename)}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch .tex file');
  }

  return response.text();   // LaTeX source string
}

/**
 * GET /download-pdf/:fileId  — triggers browser download via location redirect
 */
export function triggerPdfDownload(fileId, pdfFilename) {
  window.location.href = `${BASE_URL}/download-pdf/${fileId}?download_name=${encodeURIComponent(pdfFilename)}`;
}

/**
 * Download the current editor LaTeX code as a .tex blob client-side.
 */
export function downloadTexBlob(latexCode, filename) {
  const blob = new Blob([latexCode], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * POST /find-jobs  — fetches live job market data matching the profile
 */
export async function findJobs(analysisData, filters = {}) {
  const response = await fetch(`${BASE_URL}/find-jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_data: analysisData, filters }),
  });

  const json = await response.json();

  if (!response.ok || !json.success) {
    throw new Error(json.error ?? 'Job search failed');
  }

  return json;
}
