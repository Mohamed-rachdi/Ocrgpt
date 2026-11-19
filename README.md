# OCR GPT

A small Flask web app that turns images and PDFs into text — and lets you ask an AI questions about the document you just uploaded.

Upload a scan, a photo of a page or a PDF, and OCR GPT extracts the text, shows it in the browser, and lets you copy it or download it as a **PDF** or a **Word** document. A second page sends the extracted text to the OpenAI API together with your own question, so you can summarize a document, answer exam questions or explain a contract without retyping anything.

---

## Features

- **Image → text** — OCR on images with Tesseract (`pytesseract` + `Pillow`).
- **PDF → text** — direct text extraction with `pdfplumber` (no OCR needed for digital PDFs).
- **Text → Word** — the extracted text is written to a `.docx` file you can download.
- **Text → PDF** — client-side export with jsPDF.
- **Copy to clipboard** — one button, with a fallback for older browsers.
- **Document chatbot** — ask a question about the uploaded file; the question and the extracted text are sent to the OpenAI API and the answer is displayed.
- **Image → Excel** — page exists (`/imexcel`) but the feature is **not implemented yet** (see [Known limitations](#known-limitations)).

## Tech stack

| Layer    | Technology                                           |
|----------|------------------------------------------------------|
| Backend  | Python 3, Flask                                       |
| OCR      | Tesseract OCR via `pytesseract`, `Pillow`             |
| PDF      | `pdfplumber`                                          |
| Word     | `python-docx`                                         |
| AI       | OpenAI API (`openai`)                                 |
| Frontend | HTML, CSS, vanilla JavaScript, jsPDF, Font Awesome, Animate.css |

## Project structure

```
ocrGpt/
├── app.py                 # Flask app: routes, OCR, PDF parsing, OpenAI call
├── requerement.txt        # dependency list (see Installation)
├── templates/
│   ├── index.html         # OCR page: upload → text → copy / PDF / Word
│   ├── chatbot.html       # ask a question about the uploaded document
│   └── imexcel.html       # image → Excel (placeholder)
├── static/
│   ├── style.css
│   └── logo.png
└── word_docs/
    └── output.docx        # generated Word file (overwritten on each scan)
```

## Requirements

- Python 3.8+
- **Tesseract OCR installed on the machine** ([Windows builds](https://github.com/UB-Mannheim/tesseract/wiki), or `apt install tesseract-ocr` / `brew install tesseract`)
- An OpenAI API key (only needed for the chatbot page)

## Installation

```bash
git clone https://github.com/<your-username>/ocrGpt.git
cd ocrGpt

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install Flask openai pdfplumber Pillow pytesseract python-docx
```

> `requerement.txt` is a plain list of `pip install` commands, not a pip requirements file, and it is missing `python-docx`. Use the command above, or create a proper `requirements.txt` and run `pip install -r requirements.txt`.

## Configuration

**1. Tesseract path.** `app.py` points to a hardcoded Windows path:

```python
pytesseract.pytesseract.tesseract_cmd = r'E:\update\beta 1.8\packages\tessr\tesseract.exe'
```

Change it to your own installation (`C:\Program Files\Tesseract-OCR\tesseract.exe` on Windows), or delete the line entirely if `tesseract` is already on your `PATH`.

**2. OpenAI API key.** The key is currently written directly in `app.py`. Read it from the environment instead:

```python
import os
openai.api_key = os.environ["OPENAI_API_KEY"]
```

Then set it before starting the app:

```bash
# macOS / Linux
export OPENAI_API_KEY="sk-..."
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
```

## Running the app

```bash
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

> `app.py` runs `activate_venv.bat` at import time. That file is not in the repository, and the call is Windows-only — remove the first lines of `app.py` if the app fails to start.

## Pages and endpoints

| Method | Route            | What it does                                                                 |
|--------|------------------|------------------------------------------------------------------------------|
| GET    | `/`              | OCR page: upload an image or PDF and read the extracted text                  |
| GET    | `/chatbot`       | Ask a question about an uploaded document                                     |
| GET    | `/imexcel`       | Image → Excel page (not functional)                                           |
| POST   | `/uploadI`       | Extracts the text, writes `word_docs/output.docx`, returns `{"text": "..."}`  |
| POST   | `/upload`        | Extracts the text, sends it with `prompt_text` to OpenAI, returns `{"generated_text": "..."}` |
| GET    | `/download_word` | Downloads the last generated Word document                                    |

## How it works

1. The uploaded file is saved to a temporary file on the server.
2. If the filename ends with `.pdf`, text is read page by page with `pdfplumber`; otherwise the image goes through Tesseract (`lang='eng'`).
3. On `/uploadI`, the text is written to a Word document and returned as JSON for display.
4. On `/upload`, the first 4000 characters of the text are appended to the user's question and sent to the OpenAI completion endpoint; the answer is returned as JSON.

## Known limitations

- **Image → Excel is not implemented.** The front end shows "service currently unavailable" and calls `/upload`, while the template expects a `download_excel` route that does not exist in `app.py`.
- **OCR language is fixed to English** (`lang='eng'`). Add other languages by installing the matching Tesseract data and passing e.g. `lang='fra+ara'`.
- **One shared output file.** Every scan overwrites `word_docs/output.docx`, so concurrent users would download each other's documents.
- **Deprecated OpenAI usage.** The code uses `openai.Completion.create(engine="davinci")`, which belongs to the legacy SDK (`openai<1.0`) and a retired model. On the current SDK the call becomes:

  ```python
  from openai import OpenAI
  client = OpenAI()
  answer = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
  ).choices[0].message.content
  ```

- **No validation or error handling.** Empty PDF pages make `page.extract_text()` return `None` and raise; file type and size are not checked; the temporary file created in `/uploadI` is never deleted.
- **Not production-ready.** The Flask development server has no authentication, rate limiting or HTTPS.

## Roadmap

- [ ] Implement image → Excel (table detection + `openpyxl`)
- [ ] Multi-language OCR, selectable from the interface
- [ ] Per-user / per-session output files instead of a single `output.docx`
- [ ] Migrate to the current OpenAI SDK and a supported model
- [ ] Proper `requirements.txt` and `.gitignore`
- [ ] Input validation, error messages and tests
- [ ] Dockerfile for one-command deployment

## Security

The repository contains a **hardcoded OpenAI API key** in `app.py`. If that key is still active, revoke it in the OpenAI dashboard, generate a new one, and load it from an environment variable as shown in [Configuration](#configuration). Removing the line is not enough on its own — the key stays readable in the Git history, so rotate it.

Add a `.gitignore` before committing again:

```gitignore
venv/
__pycache__/
.env
word_docs/*.docx
```

## License

No license file is included yet. Add one (MIT is a common choice) if you want others to reuse the code.
