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

## Deploy to Render

Deploy this project as a Render **Web Service** (not a Static Site), because FastAPI loads the model and serves both the page and API.

1. Push the project to GitHub, including `requirements.txt`, `.gitattributes`, and the `saved_model_summary/` model files. Confirm `git lfs ls-files` lists `saved_model_summary/model.safetensors`.
2. In the Render Dashboard, select **New > Web Service** and connect the GitHub repository.
3. Use the repository root as the root directory, choose the Python runtime, and set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Choose an instance with enough memory for the model and inference. The checkpoint alone is about 990 MB; the running model needs additional memory. Render's 512 MB free web service is not sufficient. Check current Render instance plans and choose one with several GB of RAM.
5. Create the service and check its deploy logs. When it is live, open the `onrender.com` URL. The interactive UI is at `/`, and API docs are at `/docs`.

The checkpoint uses Git LFS, so make sure the GitHub LFS quota allows Render to download it during deployment. If the build or startup reports missing or invalid model files, verify that the LFS files were pushed and that the deployed checkout contains the actual model files, not LFS pointer text. Keep in mind that free services can spin down when idle; model loading may make the first request after a spin-down slow.

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
