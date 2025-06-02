from sqlalchemy import Column, Integer, String
from api.database import Base



class ArticleSummary(Base):
    __tablename__ = "article_summaries"

    id = Column(Integer, primary_key=True, index=True)
    
    summary = Column(String, nullable=False)
    
    
    