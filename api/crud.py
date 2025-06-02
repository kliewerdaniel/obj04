import ollama
from sqlalchemy.orm import Session
from .models import ArticleSummary

def create_article_summary(db: Session, summary: str):
    db_summary = ArticleSummary(summary=summary)
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def generate_broadcast_content(db: Session):
    # Fetch all summaries
    summaries = db.query(ArticleSummary.summary).all()
    combined = "\n\n".join(summary[0] for summary in summaries)
    # Call Ollama model
    prompt = f"Create an objective news broadcast in formal tone based on these summaries:\n\n{combined}"
    response = ollama.chat(
        model='phi4-reasoning:latest',
        messages=[{"role": "user", "content": prompt}]
    )
    news_broadcast = response['message']['content']
    return {"broadcast": news_broadcast}
