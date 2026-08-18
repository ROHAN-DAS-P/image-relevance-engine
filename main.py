from fastapi import FastAPI
from app.database import engine, Base, init_db
from app.config import settings
from app.models import Image, ImageMetadata, Post, Match, AICostLog

# Initialize extensions and tables
init_db()

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image Relevance Engine")

@app.get("/health")
def health_check():
    # Never return the actual API key in a response, just verify it's loaded
    gemini_configured = bool(settings.GEMINI_API_KEY)
    
    return {
        "status": "ok", 
        "database_connected": True,
        "gemini_configured": gemini_configured
    }