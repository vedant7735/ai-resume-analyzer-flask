from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

# Import services
from services.pdf_service import extract_text_from_pdf
from services.cleaner_service import clean_text
from services.llm_service import analyze_resume
from services.latex_service import generate_improved_latex, save_latex_and_pdf
from services.cache_service import get_file_hash, get_cached_analysis, save_to_cache

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
CACHE_FOLDER = 'cache'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/styles.css')
def style():
    return send_from_directory('templates', 'styles.css')


@app.route('/script.js')
def script():
    return send_from_directory('templates', 'script.js')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and analysis"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    filepath = None
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check cache
        file_hash = get_file_hash(filepath)
        cached = get_cached_analysis(file_hash, CACHE_FOLDER)
        
        if cached:
            os.remove(filepath)
            return jsonify({
                'success': True,
                'filename': filename,
                'data': cached,
                'cached': True
            }), 200
        
        # Extract and clean
        raw_text = extract_text_from_pdf(filepath)
        cleaned_text = clean_text(raw_text)
        
        # Analyze with LLM
        result = analyze_resume(cleaned_text)
        
        # Cache result
        save_to_cache(file_hash, result, CACHE_FOLDER)
        
        # Cleanup
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'data': result,
            'cached': False
        }), 200
        
    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500


@app.route('/generate-latex', methods=['POST'])
def generate_latex():
    """Generate improved LaTeX resume and compile PDF if possible"""
    
    try:
        data = request.json
        resume_data = data.get('resume_data')
        
        if not resume_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate LaTeX
        latex_code = generate_improved_latex(resume_data, "")
        
        # Save LaTeX and compile to PDF
        file_info = save_latex_and_pdf(latex_code, GENERATED_FOLDER)
        
        return jsonify({
            'success': True,
            'file_id': file_info['file_id'],
            'filename': file_info['tex_filename'],
            'pdf_available': bool(file_info['pdf_filepath'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-latex/<file_id>')
def download_latex(file_id):
    """Download LaTeX file"""
    filename = f"resume_{file_id}.tex"
    return send_from_directory(GENERATED_FOLDER, filename, as_attachment=True)


@app.route('/download-pdf/<file_id>')
def download_pdf(file_id):
    """Download PDF file"""
    filename = f"resume_{file_id}.pdf"
    return send_from_directory(GENERATED_FOLDER, filename, as_attachment=True)

@app.route('/debug-latex', methods=['POST'])
def debug_latex():
    """Debug route - see raw LLM output"""
    try:
        from services.latex_service import format_resume_data, IMPROVEMENT_PROMPT
        import os
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        data = request.json
        resume_data = data.get('resume_data')
        data_str = format_resume_data(resume_data)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": IMPROVEMENT_PROMPT},
                {"role": "user", "content": f"Improve and return this resume content:\n\n{data_str}"}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content

        # Return raw so you can inspect it
        return jsonify({
            'raw_output': raw
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)