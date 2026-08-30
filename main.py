from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import engine, Base, init_db, get_db
from app.config import settings
from app.jobs import process_pending_images
from app.models import Image, ImageMetadata, Post, Match, AICostLog
from app.services.matching import match_images_for_post

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


@app.get("/api/posts/{post_id}/images")
def get_image_suggestions(post_id: str, db: Session = Depends(get_db)):
    """
    Ranks images for a specific post and runs them through the Mismatch Guard.
    """
    # Verify the post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"error": "Post not found"}
        
    results = match_images_for_post(post_id, db)
    
    # If no images passed the hard similarity threshold
    if not results or all(r["status"] == "guarded_mismatch" for r in results):
        return {
            "post_title": post.title,
            "message": "No confident match found. Similarity below threshold or detected subjects do not match article topic.",
            "candidates_reviewed": results
        }
        
    return {
        "post_title": post.title,
        "suggestions": results
    }

@app.post("/api/jobs/process-images")
def trigger_image_processing(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers the async vision AI batch job."""
    
    # We pass the function to FastAPI to run AFTER it returns the 202 Accepted response
    background_tasks.add_task(process_pending_images, db)
    
    return {"message": "Batch processing started in the background."}