from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename

# Configure the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Gemini API Configuration
API_KEY = "AIzaSyAA-nzQcukB2ETHR63X81Iy5XCCLogkbzI"  # Securely store API keys in environment variables for production
genai.configure(api_key=API_KEY)

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def upload_file(file):
    # Save the uploaded file to the upload folder
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part", 400

        pdf_file = request.files['pdf_file']

        if pdf_file and allowed_file(pdf_file.filename):
            file_path = upload_file(pdf_file)

            # Generate MCQs using Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Upload the PDF file and process it 
            sample_file = genai.upload_file(path=file_path, display_name="Uploaded PDF")
            print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

            # Generate MCQs from the file
            prompt = "Generate 10 math MCQs of only problem type with integration symbols based on the file.Give mathematical equations and symbols in latex format but dont include $ sign.Separate each mcq by 'MCQ'.remove all dollar signs"
            response = model.generate_content([sample_file, prompt])
            print(response)
            # Process the response and wrap the MCQs with LaTeX block math format
            mcqs = [f"\({mcq.strip()}\)" for mcq in response.text.split("MCQ")]  # Add $$ for block LaTeX
            session['mcqs'] = mcqs
            return redirect(url_for('display_mcqs'))

    return render_template('index.html')

@app.route('/mcqs')
def display_mcqs():
    mcqs = session.get('mcqs', [])
    return render_template('mcqs.html', mcqs=mcqs)

if __name__ == '__main__':
    app.run(debug=True)
