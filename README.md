## Technique Generator — Step‑by‑Step Quick Start (Non‑Technical)

Follow these steps exactly to run the app and generate techniques. No coding required.

### 1) Install prerequisites
- Make sure Python is installed.
  - Windows: download "Python 3" from the official site and complete install.
  - macOS/Linux: Python 3 is usually available. If not, install it first.

### 2) Open the project folder
- Locate the project folder on your computer.
- Open a terminal (Windows PowerShell, macOS Terminal, or Linux shell) in that folder.

### 3) Install the app
Run this command in the terminal:
```bash
pip install -r requirements.txt
```
If you see an error about pip, try:
```bash
python -m pip install -r requirements.txt
```

### 4) Start the app
Run this command in the terminal:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Leave this window open while you use the app.

### 5) Open the app in your browser
- Go to: `http://127.0.0.1:8000/docs`
- This opens an interactive page where you can click buttons to run actions.

### 6) Generate a technique (the main thing you want)
- On the docs page, find and click: `POST /generateTechnique`
- Click the “Try it out” button.
- Replace the example JSON with this (do not change the field names):
```json
{
  "seed": "demo-seed-1",
  "request_id": "req-1",
  "name_uniqueness_required": true
}
```
- Click “Execute”.
- What you get back is your technique:
  - `human_text`: formatted text you can read or display
  - `machine_data`: the exact structured data

That’s it — you have generated a technique.

### Optional: Validate, finalize, and save
If you want to go further (optional):
1) Validate
- Click `POST /validateTechnique` → “Try it out”.
- Paste the `machine_data` and `human_text` you just received.
- Click “Execute”. If `pass` is true and the score is high enough, you can finalize.

2) Finalize
- Click `POST /finalizeTechnique` → “Try it out”.
- Paste `machine_data` and `human_text` again.
- For `attempts_history`, paste the validation result you got in step 1 inside an array, like this:
```json
[
  { "pass": true, "score": 98.0 }
]
```
- Click “Execute”. If it says `final_validated`, it’s ready to save.

3) Save (Ingest)
- Click `POST /ingestTechnique` → “Try it out”.
- Paste the same `machine_data` and `human_text`.
- Click “Execute”. You’ll get an `ingestion_log_id` confirming it was saved.

### Optional: Enable Gemini (for smarter audits)
Only if you have a Gemini API key (not required to generate techniques):
- Windows PowerShell: `$env:GEMINI_API_KEY="your-key"`
- macOS/Linux: `export GEMINI_API_KEY="your-key"`
Then start the app again (step 4).

### Troubleshooting
- The page won’t open
  - Make sure you used `http://127.0.0.1:8000/docs` and the app is still running in the terminal.
- Pip errors
  - Try `python -m pip install -r requirements.txt` instead of `pip`.
- Still stuck?
  - Close the app (Ctrl+C in the terminal) and repeat steps 3–5.