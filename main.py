# Apply feedparser patch BEFORE importing anything else
import feedparser_patch # Add this at the very top

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.graph import router as graph_router

# Import necessary modules for the pipeline
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from api.database import SessionLocal, engine, get_db
from api.models import ArticleSummary
from api.models import Base  # Import your SQLAlchemy models
from api import broadcast
from modules.scraping import fetch_articles
from modules.translation import translate_article
from modules.summarization import summarize
from api.crud import create_article_summary # Import create_article_summary
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In dev. Lock it down in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(broadcast.router, prefix="/api")


# Include the router mounted at /api/graph
app.include_router(graph_router, prefix="/api/graph")

# Serve static files (e.g. your graph.html page)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the static audio directory
app.mount("/static/audio", StaticFiles(directory="static/audio"), name="audio")

@app.get("/graph")
def serve_graph_page():
    return FileResponse("static/graph.html")

def create_article_summary(db: Session, summary: str):
    new_summary = ArticleSummary(summary=summary)
    db.add(new_summary)
    db.commit()

@app.get("/api/run_pipeline")
def run_pipeline():
    print("🚀 Starting news pipeline...")

    try:
        # Step 1: Scrape
        print("📰 Scraping articles...")
        articles = fetch_articles(max_articles=1) # Use the updated max_articles

        # Step 2: Process each article
        results = []
        for article in articles:
            print(f"🔍 Processing: {article['title']}")

            # Translate if needed
            article['translated_text'] = translate_article(article)

            # Summarize
            article['summary'] = summarize(article['translated_text'])

            results.append({
                'title': article['title'],
                'source': article['source'],
                'summary': article['summary'],
                'url': article['url'],
                'published': article['published']
            })

        # Step 3: Output
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join('output', f'news_digest_{timestamp}.json') # Correct path

        print("📝 Final results before saving:") # Add logging
        print(json.dumps(results, indent=2)) # Print the results

        # Step 3: Save to database
        print("💾 Saving summaries to database...")
        db: Session = next(get_db()) # Get a database session
        for article_data in results:
            create_article_summary(db, summary=article_data['summary'])
        db.close() # Close the session

        # Step 4: Output (optional, for debugging/archiving)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Pipeline complete! Output saved to {output_file} and summaries saved to database.")
        print(f"📊 Processed {len(results)} articles")

        return {"status": "success", "message": "Pipeline executed successfully."}

    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        return {"status": "error", "message": str(e)}
