# EduAdapt AI — Hackathon MVP

A local Flask web app demonstrating:
1. Source-cited search across uploaded PDFs, PPTX slides, TXT/MD notes and timestamped lecture transcripts.
2. Automatically generated, source-grounded keyword/cloze quizzes with easy/medium/hard/adaptive modes.
3. A learning-gap dashboard that recommends revision from saved quiz results.

## Important scope note
This MVP uses TF-IDF retrieval, not a hosted LLM. Tutor answers quote relevant retrieved passages and cite the filename plus page/slide/timestamp. This is intentionally transparent and avoids pretending an AI answer is supported when no source passage is found. Quiz questions are generated with a lightweight keyword/cloze method; review them before using them for graded assessments.

## Windows / VS Code setup
1. Install Python 3.11 or 3.12 and VS Code.
2. Extract the ZIP. In VS Code choose **File → Open Folder** and select `eduadapt_ai`.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
6. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
7. Run:
   ```powershell
   python app.py
   ```
8. Open `http://127.0.0.1:5000` in your browser.

## First test
- Upload `sample_data/machine_learning_notes.txt`.
- Open **AI Tutor**, ask: `What is overfitting?`
- Open **Adaptive Quiz**, choose `overfitting` or leave the topic blank, then generate a quiz.
- Submit the quiz and visit **Learning Gaps**.

## Accepted uploads
- PDF: text-based PDFs. Scanned/image-only PDFs need OCR before upload.
- PPTX: text in slide shapes.
- TXT / MD: plain text and lecture transcripts. For video timestamps, format lines like `[00:03:12] Overfitting occurs when...`.
- Max upload size: 20 MB.

## Dataset
`sample_data/machine_learning_notes.txt` is a small original demo corpus, not a third-party benchmark. Upload your own permitted course notes, slides, textbook excerpts, and transcripts for your hackathon demo. Use public-domain/open-licensed course resources and check the license before redistributing them. No separate ML training dataset is required for this retrieval-based prototype.

## Project layout
- `app.py`: Flask routes, upload handling, SQLite history.
- `tutor_engine.py`: document extraction, TF-IDF retrieval, quiz generation and revision logic.
- `templates/`: pages.
- `static/style.css`: interface styling.
- `sample_data/`: starter learning material.
- `uploads/`: files uploaded by users (created automatically).
- `eduadapt.db`: local SQLite database (created automatically).

## Before public deployment
Set a strong `SECRET_KEY`, add authentication and per-user access controls, validate uploads more strictly, add rate limits, malware scanning, backups, and privacy/retention controls. Do not upload copyrighted materials unless you have permission.
