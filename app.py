from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import hashlib

from backend.services.model_service.extractors.multimodal_extractor import (
    SUPPORTED_EXTENSIONS,
    extract_resume,
    get_resume_input_type
)
from backend.services.model_service.operations.llm_call import run_single_pass
from backend.services.jobs.job_search_service import search_live_jobs
from backend.services.rendering.renderer import render_to_latex, compile_latex_to_pdf
from backend.services.caching.cache_service import (
    get_file_hash, 
    get_cached_analysis, 
    save_to_cache,
    get_cached_enhancement,
    save_enhancement_to_cache,
    get_cached_render,
    save_render_to_cache
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'backend/uploads'
CACHE_FOLDER = 'backend/cache'
GENERATED_FOLDER = 'backend/generated'
ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

for folder in [UPLOAD_FOLDER, CACHE_FOLDER, GENERATED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_download_basename(resume):
    identity = (resume or {}).get('identity', {})
    candidate_name = (identity.get('name') or 'candidate').strip()
    safe_name = secure_filename(candidate_name.replace(' ', '_')).strip('_')

    if not safe_name:
        safe_name = 'candidate'

    return f"{safe_name}_resume_ai_pack"

# ---------------------------------------------------------------
# MIGRATED TO REACT — these routes are no longer served by Flask.
# The React SPA (client/) handles all UI. Keep for reference only.
# ---------------------------------------------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/styles.css')
# def style():
#     return send_from_directory('templates', 'styles.css')
#
# @app.route('/script.js')
# def script():
#     return send_from_directory('templates', 'script.js')
# ---------------------------------------------------------------

# Pipeline routes
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    filepath = None
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        jd_text = None
        if request.form.get("jd_text", "").strip():
            jd_text = request.form["jd_text"].strip()
        elif "jd_file" in request.files:
            jd_file = request.files["jd_file"]
            if jd_file and jd_file.filename:
                jd_text = jd_file.read().decode("utf-8", errors="ignore").strip()

        input_type = get_resume_input_type(filename)
        file_hash = get_file_hash(filepath)
        
        if jd_text:
            import hashlib
            jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
            file_hash = f"{file_hash}_{jd_hash[:8]}"

        cached_v2 = get_cached_analysis(file_hash, CACHE_FOLDER)
        
        if cached_v2:
            os.remove(filepath)
            return jsonify({
                'success': True,
                'data': cached_v2,
                'cached': True,
                'input_type': input_type
            }), 200

        resume_v1 = extract_resume(filepath, filename)
        # The new run_single_pass takes raw text. extract_resume returns a dict.
        resume_v2 = run_single_pass(json.dumps(resume_v1), jd_text=jd_text)
        
        if jd_text is None and resume_v2.get("jd_match") is not None:
            resume_v2["jd_match"] = None
            
        save_to_cache(file_hash, resume_v2, CACHE_FOLDER)
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'data': resume_v2,
            'cached': False,
            'input_type': input_type
        }), 200
        
    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/find-jobs', methods=['POST'])
def find_jobs():
    try:
        analysis_data = request.json.get('analysis_data')
        filters = request.json.get('filters', {})
        if not analysis_data:
            return jsonify({'error': 'No analysis data provided'}), 400
            
        result = search_live_jobs(analysis_data, filters)
        
        # result is a dict: {jobs, relaxed_filters, applied_filters}
        # Handle legacy list returns just in case
        if isinstance(result, list):
            result = {'jobs': result, 'relaxed_filters': False, 'applied_filters': {}}
        
        return jsonify({
            'success': True,
            'jobs': result.get('jobs', []),
            'relaxed_filters': result.get('relaxed_filters', False),
            'applied_filters': result.get('applied_filters', {})
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/enhance', methods=['POST'])
def enhance():

    try:

        resume_v2 = request.json.get('resume')

        if not resume_v2:
            return jsonify({
                'error': 'No resume data'
            }), 400

        # The new architecture unifies analyze and enhance. 
        # resume_v2 is already enhanced from the initial upload pass.
        resume_v3 = resume_v2

        # -----------------------------
        # Render Cache
        # -----------------------------

        cached_render = get_cached_render(
            resume_v3,
            CACHE_FOLDER
        )

        if cached_render:

            pdf_exists = (
                cached_render['pdf_path'] is not None
                and
                os.path.exists(cached_render['pdf_path'])
            )

            if pdf_exists:
                download_basename = build_download_basename(resume_v3)
                return jsonify({
                    'success': True,
                    'file_id': cached_render['file_id'],
                    'tex_filename': f"{download_basename}.tex",
                    'pdf_filename': f"{download_basename}.pdf",
                    'download_basename': download_basename,
                    'pdf_available': True,
                    'cached': True
                }), 200

        # -----------------------------
        # Render Fresh Files
        # -----------------------------

        latex_code = render_to_latex(resume_v3)

        tex_path, pdf_path, file_id = compile_latex_to_pdf(
            latex_code,
            GENERATED_FOLDER
        )

        print("TEX PATH:", tex_path)
        print("PDF PATH:", pdf_path)
        print(
            "PDF EXISTS:",
            os.path.exists(pdf_path)
            if pdf_path else False
        )

        save_render_to_cache(
            resume_v3,
            tex_path,
            pdf_path,
            file_id,
            CACHE_FOLDER
        )

        pdf_exists = (
            pdf_path is not None
            and
            os.path.exists(pdf_path)
        )

        download_basename = build_download_basename(resume_v3)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'tex_filename': f"{download_basename}.tex",
            'pdf_filename': (
                f"{download_basename}.pdf"
                if pdf_exists else None
            ),
            'download_basename': download_basename,
            'pdf_available': pdf_exists,
            'cached': False
        }), 200

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/compile-latex', methods=['POST'])
def compile_latex():
    try:
        latex_code = request.json.get('latex_code')
        if not latex_code:
            return jsonify({'error': 'No LaTeX code provided'}), 400

        tex_path, pdf_path, file_id = compile_latex_to_pdf(
            latex_code,
            GENERATED_FOLDER
        )

        pdf_exists = pdf_path is not None and os.path.exists(pdf_path)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'tex_filename': f"resume_{file_id}.tex",
            'pdf_filename': f"resume_{file_id}.pdf" if pdf_exists else None,
            'download_basename': f"resume_{file_id}",
            'pdf_available': pdf_exists,
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download-tex/<file_id>')
def download_tex(file_id):
    download_name = request.args.get(
        'download_name',
        f"resume_{file_id}.tex"
    )
    return send_from_directory(
        GENERATED_FOLDER,
        f"resume_{file_id}.tex",
        as_attachment=True,
        download_name=download_name
    )

@app.route('/download-pdf/<file_id>')
def download_pdf(file_id):
    download_name = request.args.get(
        'download_name',
        f"resume_{file_id}.pdf"
    )
    return send_from_directory(
        GENERATED_FOLDER,
        f"resume_{file_id}.pdf",
        as_attachment=True,
        download_name=download_name
    )

if __name__ == '__main__':
    app.run(debug=True)
