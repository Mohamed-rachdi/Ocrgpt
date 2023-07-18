import os

import subprocess

activate_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), "activate_venv.bat")
subprocess.call(activate_script, shell=True)

from flask import Flask, render_template, request, jsonify, url_for
import tempfile
import pdfplumber
import openai
from PIL import Image
import pytesseract
from docx import Document

app = Flask(__name__)



pytesseract.pytesseract.tesseract_cmd = r'E:\update\beta 1.8\packages\tessr\tesseract.exe'


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/imexcel')
def imexcel():
    return render_template('imexcel.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploadI', methods=['POST'])
def uploadI():
    if 'file' not in request.files:
        return 'No file uploaded'

    file = request.files['file']
    if file.filename == '':
        return 'No file selected'

    # Save the uploaded file to a temporary location on the server
    fd, file_path = tempfile.mkstemp()
    os.close(fd)
    file.save(file_path)

    # Check the file type
    if file.filename.endswith('.pdf'):
        # Load the PDF and extract the text using pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages = pdf.pages
            text = ''
            for page in pages:
                text += page.extract_text()

    else:
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang='eng')
    
     # Create a new Word document
    document = Document()

    # Add the text to the document
    document.add_paragraph(text)

    # Save the document to the "word_docs" directory within the app directory
    word_dir = os.path.join(app.root_path, 'word_docs')
    if not os.path.exists(word_dir):
        os.makedirs(word_dir)
    word_path = os.path.join(word_dir, 'output.docx')
    document.save(word_path)

    # Return response as a JSON object with the text and a download link for the Word document
    response = {'text': text }

    return jsonify(response)

from flask import send_file

@app.route('/download_word')
def download_word():
    word_path = os.path.join(app.root_path, 'word_docs', 'output.docx')
    return send_file(word_path, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file uploaded'

    file = request.files['file']
    if file.filename == '':
        return 'No file selected'

    # Save the uploaded file to a temporary location on the server
    fd, file_path = tempfile.mkstemp()
    os.close(fd)
    file.save(file_path)

    # Check the file type
    if file.filename.endswith('.pdf'):
        # Load the PDF and extract the text using pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages = pdf.pages
            text = ''
            for page in pages:
                text += page.extract_text()

    else:
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang='eng')

    # Set the OpenAI API key
    openai.api_key = "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"
    question = request.form['prompt_text']

    # Run the model on the extracted text using OpenAI API
    prompt = f"{question} : '{text[:4000]}'"
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=500
    )
    # Extract the generated text from the response object and format it
    generated_text = response.choices[0].text.strip()

    # Return response as a JSON object
    response = {'generated_text': generated_text}

    # Remove the temporary file
    os.remove(file_path)

    return jsonify(response)

if __name__ == '__main__':
    app.run()
