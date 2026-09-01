from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import engine, Base, init_db, get_db
from app.config import settings
from app.jobs import process_pending_images
from app.models import Image, ImageMetadata, Post, Match, AICostLog
from app.services.matching import match_images_for_post


class RejectPayload(BaseModel):
    reason: str

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


@app.post("/api/posts/{post_id}/images/{image_id}/approve")
def approve_match(post_id: str, image_id: str, db: Session = Depends(get_db)):
    """Allows a human editor to approve an AI image suggestion."""
    match = db.query(Match).filter_by(post_id=post_id, image_id=image_id).first()
    
    if not match:
        # If it wasn't saved yet, create the record
        match = Match(post_id=post_id, image_id=image_id, similarity_score=1.0, status="approved")
        db.add(match)
    else:
        match.status = "approved"
        
    db.commit()
    return {"message": "Image approved successfully", "post_id": post_id, "image_id": image_id}

@app.post("/api/posts/{post_id}/images/{image_id}/reject")
def reject_match(post_id: str, image_id: str, payload: RejectPayload, db: Session = Depends(get_db)):
    """Allows a human editor to reject an AI image suggestion with a reason."""
    match = db.query(Match).filter_by(post_id=post_id, image_id=image_id).first()
    
    if not match:
        match = Match(
            post_id=post_id, 
            image_id=image_id, 
            similarity_score=0.0, 
            status="rejected", 
            rejection_reason=payload.reason
        )
        db.add(match)
    else:
        match.status = "rejected"
        match.rejection_reason = payload.reason
        
    db.commit()
    return {"message": "Image rejected successfully", "reason": payload.reason}