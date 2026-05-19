from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import PyPDF2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Add this line

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file is a PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_resume_text(pdf_path):
    """Extract text from resume PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/styles.css')
def style():
    """Serve the CSS file"""
    return send_from_directory('templates', 'styles.css')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and extraction"""
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is PDF
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save file securely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text
        extracted_text = extract_resume_text(filepath)
        
        # Optional: Delete file after extraction
        os.remove(filepath)
        
        # Return extracted text
        return jsonify({
            'success': True,
            'filename': filename,
            'text': extracted_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-multiple', methods=['POST'])
def upload_multiple():
    """Handle multiple PDF uploads"""
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract text
                extracted_text = extract_resume_text(filepath)
                
                # Optional: Delete file after extraction
                os.remove(filepath)
                
                results.append({
                    'filename': filename,
                    'success': True,
                    'text': extracted_text
                })
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
    
    return jsonify({'results': results}), 200

if __name__ == '__main__':
    app.run(debug=True)