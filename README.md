# Agentic Document Extraction
Goal: ingest documents (PDF/image), detect type (invoice, medical_bill, prescription), extract structured key-value JSON with per-field confidence and overall score, validate with cross-field rules, and provide a Streamlit UI for uploads and experimentation.

## Features
- Upload PDF or image (multi-page PDFs supported)
- OCR using Tesseract (`pytesseract`) + `pdf2image` for PDF conversion
- Simple routing (keyword + heuristic) to classify document type
- LLM-based structured extraction via **OpenRouter** (use `OPENROUTER_API_KEY` environment variable)
- Post-processing validations (regex, totals match)
- Per-field and overall confidence scoring
- Streamlit UI with JSON output, downloadable zip, and visual confidence bars

## Setup
1. Install Tesseract on your system (required): https://tesseract-ocr.github.io/tessdoc/Installation.html
2. Create a Python virtual environment and install dependencies:
```
pip install -r requirements.txt
```
3. Set your OpenRouter API key as an environment variable:
```
export OPENROUTER_API_KEY="your_key_here"
```
4. Run the Streamlit app:
```
streamlit run streamlit_app.py
```
## Notes
- This is a starter implementation focused on modularity and ease of experimentation. Improve LLM prompts, layout parsing, and validation rules as needed.
- The app **uses OpenRouter** (OpenRouter-compatible LLMs). The code assumes OpenRouter's standard `https://api.openrouter.ai/v1/chat/completions` endpoint; adjust if your provider differs.
