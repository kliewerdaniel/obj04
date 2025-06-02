import json
from sqlalchemy.orm import Session
from api.database import Base, engine, SessionLocal
from api import crud

def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Populate ArticleSummary with data from news_digest.json
    db: Session = SessionLocal()
    try:
        with open("output/news_digest_2025-06-02.json", "r") as f:
            articles = json.load(f)
            for article in articles:
                summary_text = article.get("summary")
                if summary_text:
                    crud.create_article_summary(db=db, summary=summary_text)
            print("Article summaries populated.")
    except FileNotFoundError:
        print("Error: output/news_digest_2025-06-02.json not found.")
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
