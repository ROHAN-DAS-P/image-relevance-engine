from sqlalchemy.orm import Session
from app.models import Image, ImageMetadata, AICostLog
from app.services.vision import analyze_image_with_gemini
import time

def process_pending_images(db: Session):
    # Find all images waiting to be processed
    pending_images = db.query(Image).filter(Image.status == "pending").all()
    
    for image in pending_images:
        image.status = "processing"
        db.commit()
        
        try:
            # 1. Send to Gemini
            print(f"Processing image: {image.filename}...")
            # result = analyze_image_with_gemini(image.url) 
            result = analyze_image_with_gemini(f"static/images/{image.filename}")
            data = result["metadata"]
            
            # 2. Flag low confidence per the Brief requirements
            if data["confidence"] < 0.70:
                print(f"⚠️ Low confidence ({data['confidence']}) for {image.filename}. Flagging for review.")
            
            # 3. Save the tags
            meta = ImageMetadata(
                image_id=image.id,
                subject=data["subject"],
                category=data["category"],
                attributes=data["attributes"],
                caption=data["caption"],
                confidence=data["confidence"]
            )
            db.add(meta)
            
            # 4. Save the cost attribution
            cost_log = AICostLog(
                job_type="vision",
                model="gemini-1.5-flash",
                tokens_used=result["tokens"],
                estimated_cost=result["cost"],
                image_id=image.id
            )
            db.add(cost_log)
            
            # Mark as done
            image.status = "processed"
            db.commit()
            print(f"✅ Success: {image.filename} tagged as {data['subject']}.")
            
            # Polite scraping/API usage limit
            time.sleep(2) 
            
        except Exception as e:
            print(f"❌ Failed to process {image.filename}: {e}")
            db.rollback()
            image.status = "failed"
            db.commit()