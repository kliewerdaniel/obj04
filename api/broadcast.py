from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import ollama
from sqlalchemy.orm import Session
from api.database import get_db  # adjust to your project structure
from .models import ArticleSummary  # your SQLAlchemy model
from .schemas import BroadcastResponse  # adjust to your project structure
from .database import get_db  # your database session dependency
from .crud import generate_broadcast_content  # adjust to your project structure
from datetime import datetime
from modules.tts import generate_audio
router = APIRouter()

class BroadcastResponse(BaseModel):
    broadcast: str
    audio_url: str | None = None

class AudioResponse(BaseModel):
    audio_url: str

class ArticleSummariesResponse(BaseModel):
    summary: List[str]

class AudioGenerationRequest(BaseModel):
    text: str

@router.get("/summaries", response_model=ArticleSummariesResponse)
def get_article_summaries(db: Session = Depends(get_db)):
    summaries = db.query(ArticleSummary.summary).all()
    # Extract the string summary from each tuple and return as a list
    return {"summary": [s[0] for s in summaries]}

@router.get("/generate_broadcast", response_model=BroadcastResponse)
def generate_broadcast(db: Session = Depends(get_db)):
    # Fetch all summaries
    summaries = db.query(ArticleSummary.summary).all()
    combined = "\n\n".join(summary[0] for summary in summaries)

    # Call Ollama model
    prompt = f"""You are an experienced news editor responsible for drafting a professional and objective news broadcast. Given a series of news story summaries, your task is to
    
    1.	Analyze the summaries for key facts, themes, and relevance.
    2.	Synthesize them into a singular, coherent, and objective news script.
    3.	Maintain a formal and journalistic tone throughout.
    4.	Avoid bias, speculation, or editorializing—stick to verified information and neutral language.

Produce the final result as a polished, ready-to-air news broadcast script.

Output only the text of the news broadcast with no symbols or text introducing or concluding the output.

    Here are the summaries to work with:

{combined}"""
    response = ollama.chat(
        model='mistral-small:24b-instruct-2501-q8_0',
        messages=[{"role": "user", "content": prompt}]
    )

    news_broadcast = response['message']['content']
    return {"broadcast": news_broadcast}

@router.post("/generate_audio", response_model=AudioResponse)
def generate_audio_endpoint(request: AudioGenerationRequest):
    try:
        # Generate a unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"broadcast_{timestamp}.mp3"
        audio_path = generate_audio(request.text, filename)
        # Return the URL relative to the static directory
        return {"audio_url": f"/static/audio/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")
