# AI-Powered Resume Analyzer

A modern, AI-driven resume analysis platform built with Flask and FastAPI. This application allows users to upload resumes and receive instant, detailed feedback on clarity, structure, missing keywords, and overall quality.

## Features

- **Modern UI**: Clean, intuitive interface using HTML, CSS, and JavaScript.
- **AI Analysis**: Built-in AI prompts to evaluate resumes against industry standards.
- **Tech Stack**: Robust backend using Flask and FastAPI.
- **File Support**: Handles PDF and DOCX resume uploads.
- **Responsive Design**: Fully accessible on desktop and mobile devices.

## Getting Started

### Prerequisites

Ensure you have Python installed. You should also set up a Python virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/vedant7735/ai-resume-analyzer-flask.git
    cd ai-resume-analyzer-flask
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once dependencies are installed, you can run the development server:

```bash
python app.py
```

Open your browser and navigate to [http://[IP_ADDRESS]](http://[IP_ADDRESS]) to use the application.

## Project Structure

```
ai-resume-analyzer-flask/
├── backend/          # FastAPI backend services
│   ├── main.py
│   └── routes/
│       └── resume.py
├── static/           # CSS and JavaScript files
├── templates/        # HTML template files
├── .env              # Environment variables (not in repo)
├── app.py            # Flask application entry point
└── requirements.txt  # Project dependencies
```
