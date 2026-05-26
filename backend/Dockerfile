FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
# - tesseract-ocr for OCR parsing
# - poppler-utils for PDF image extraction
# - texlive-latex-base and texlive-fonts-recommended for LaTeX compiling (minimal footprint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    texlive-latex-base \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose ports
EXPOSE 5000

# Set environment variable defaults
ENV FLASK_ENV=production
ENV PORT=5000

# Run via Gunicorn as WSGI server
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
