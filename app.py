import torch
import re
from pathlib import Path
from transformers import T5Tokenizer, T5ForConditionalGeneration
from fastapi import FastAPI, Request    
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates # ui ko server ke sath jhodna
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent



app = FastAPI(
    title="Text Summarization API",
    description="This is a text summarization API built using FastAPI and Hugging Face Transformers library.",
    version="1.0."
)

MODEL_DIR = BASE_DIR / "saved_model_summary"

model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)

if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
print("device:", device)

model.to(device)

templates=Jinja2Templates(directory=str(BASE_DIR))


# input schema for dialogue must be in string format
class DialogueInput(BaseModel):
    dialogue:str

def clean_data(text):
    text = re.sub(r"\r\n", " ", text) # lines
    text = re.sub(r"\s+", " ", text) # spaces
    text = re.sub(r"<.*?>", " ", text) # html tags <p> <h1>
    text = text.strip().lower()
    return text

def generate_summary(text : str):
    dialogue = clean_data(text)

    inputs=tokenizer(
        dialogue,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
        max_length=512
    ).to(device)

    model.to(device)
    target=model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=150,
        num_beams=4,
        early_stopping=True
    )
    summary=tokenizer.decode(target[0],skip_special_tokens=True)
    return summary


def detect_intent(dialogue : str):
  dialogue = clean_data(dialogue) #preprocessing

  #prompt tells the model what we want
  prompt = f"Conversation:\n{dialogue}\n\nWhat is the main intent or purpose of this conversation? Answer in one short sentence."

  inputs = tokenizer(
      prompt,
      max_length=512,
      truncation=True,
      return_tensors="pt"
  ).to(device)
  model.to(device)
  #generating the intent => token ids
  targets = model.generate(
      **inputs,
      max_new_tokens=40,
      num_beams=4,
      early_stopping=True
  )

  #token ids convert to text => decoding
  intent = tokenizer.decode(
      targets[0],
      skip_special_tokens=True
  )
  return intent

#API endpoint for text summarization
@app.post("/summarize/")
async def summarize(dialogue_input: DialogueInput):
    summary=generate_summary(dialogue_input.dialogue)
    intent=detect_intent(dialogue_input.dialogue)
    return {"summary": summary + "\n", "intent": intent}

@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse(request, "index.html", {})
