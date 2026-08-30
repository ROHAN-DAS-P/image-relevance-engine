import time
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Image, ImageMetadata, AICostLog
from app.services.vision import analyze_image_with_gemini
from app.services.embedding import generate_embedding

def process_pending_images(db: Session):
    pending_images = db.query(Image).filter(
        or_(Image.status == "pending", Image.status == "failed")
    ).all()
    
    if not pending_images:
        print("No pending or failed images to process.")
        return

    for image in pending_images:
        image.status = "processing"
        db.commit()
        
        try:
            filepath = f"static/images/{image.filename}"
            print(f"Processing image: {image.filename}...")
            
            # 1. Vision Tagging
            vision_result = analyze_image_with_gemini(filepath)
            data = vision_result["metadata"]
            
            # 2. Embedding Generation for Caption
            embed_result = generate_embedding(data["caption"])
            
            # 3. Insert or Update Metadata
            existing_meta = db.query(ImageMetadata).filter_by(image_id=image.id).first()
            if existing_meta:
                existing_meta.subject = data["subject"]
                existing_meta.category = data["category"]
                existing_meta.attributes = data["attributes"]
                existing_meta.caption = data["caption"]
                existing_meta.confidence = data["confidence"]
                existing_meta.embedding = embed_result["vector"]
            else:
                meta = ImageMetadata(
                    image_id=image.id,
                    subject=data["subject"],
                    category=data["category"],
                    attributes=data["attributes"],
                    caption=data["caption"],
                    confidence=data["confidence"],
                    embedding=embed_result["vector"]
                )
                db.add(meta)
            
            # 4. Log AI Costs (Vision + Embedding)
            db.add(AICostLog(
                job_type="vision",
                model="gemini-3.6-flash",
                tokens_used=vision_result["tokens"],
                estimated_cost=vision_result["cost"],
                image_id=image.id
            ))
            db.add(AICostLog(
                job_type="embedding",
                model="text-embedding-004",
                tokens_used=embed_result["tokens"],
                estimated_cost=embed_result["cost"],
                image_id=image.id
            ))
            
            image.status = "processed"
            db.commit()
            print(f"✅ Success: {image.filename} tagged as '{data['subject']}' with vector embedding.")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to process {image.filename}: {e}")
            db.rollback()
            image.status = "failed"
            db.commit()