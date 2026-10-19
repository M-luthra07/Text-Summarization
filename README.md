# Cleartext — Website Text Summarizer

Cleartext is a small web app that uses a locally saved T5 model to turn pasted website text into:

- **What it's for:** a short statement of the text's main intent.
- **In brief:** a concise summary of the text.

The interface is served by FastAPI, so the page and its API use the same local model.

## Features

- Dark, responsive interface for pasting website or article text.
- Summary and intent returned from one request.
- Model runs locally using PyTorch, on CUDA or Apple MPS when available, otherwise CPU.
- FastAPI endpoint for programmatic use.

## Project structure

```text
TEXT-SUMMARIZATION/
├── app.py
├── index.html
├── README.md
├── Text_Summariztion_model.ipynb
└── saved_model_summary/
    ├── config.json
    ├── model.safetensors
    └── tokenizer files
```

The notebook filename retains its current spelling.

## Requirements

- Python 3.10 or newer
- The trained model and tokenizer files in `saved_model_summary/`
- PyTorch-compatible hardware; a GPU is optional

## Setup and run

Run these commands from the project folder.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" torch transformers sentencepiece jinja2
python -m uvicorn app:app --reload
```

If PowerShell does not allow activation, you can skip the activation command and run the install and Uvicorn commands with the virtual environment's Python:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" torch transformers sentencepiece jinja2
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Keep the terminal running while you use the app. The API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

For CUDA-enabled PyTorch, use the install command recommended by the [official PyTorch installation selector](https://pytorch.org/get-started/locally/) for your operating system and CUDA version.

## API

### `POST /summarize/`

Request JSON:

```json
{
  "dialogue": "Paste the website or article text here."
}
```

Example response:

```json
{
  "summary": "A concise summary of the submitted text.\n",
  "intent": "The main purpose of the submitted text."
}
```

Example with `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/summarize/" \
  -H "Content-Type: application/json" \
  -d "{\"dialogue\":\"Paste the website or article text here.\"}"
```

The current preprocessing removes HTML-like tags, collapses whitespace, and lowercases text. Model inputs are truncated to a maximum of 512 tokens, so long pages may not be analyzed in full.

## Model files and GitHub

The trained checkpoint is required at runtime. The `model.safetensors` file is very large and exceeds GitHub's regular file-size limit. Before pushing the checkpoint, consider Git Large File Storage (Git LFS):

```bash
git lfs install
git lfs track "saved_model_summary/model.safetensors"
git add .gitattributes saved_model_summary/model.safetensors
```

Git LFS has storage and bandwidth quotas. Alternatively, keep the checkpoint outside the repository and provide instructions for obtaining it. Do not upload a model unless you have the rights to distribute it.

## Notes

- The model loads when the FastAPI application starts. If files are missing or incompatible, startup will fail.
- Intent and summary quality depend on the training data and model. Review generated text for accuracy before relying on it.
- Install the PyTorch build suited to your machine if the default package does not support your GPU.
