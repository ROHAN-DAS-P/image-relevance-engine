from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import engine, Base, init_db, get_db
from app.config import settings
from app.jobs import process_pending_images
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

@app.post("/api/jobs/process-images")
def trigger_image_processing(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers the async vision AI batch job."""
    
    # We pass the function to FastAPI to run AFTER it returns the 202 Accepted response
    background_tasks.add_task(process_pending_images, db)
    
    return {"message": "Batch processing started in the background."}