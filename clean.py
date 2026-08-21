from app.database import SessionLocal
from app.models import Image, ImageMetadata, AICostLog

def hard_reset():
    db = SessionLocal()
    
    # 1. Wipe all extracted data
    db.query(ImageMetadata).delete()
    db.query(AICostLog).delete()
    
    # 2. Reset all images to pending
    db.query(Image).update({Image.status: 'pending'})
    
    db.commit()
    db.close()
    print("✅ Hard reset complete. Zero metadata, all images pending.")

if __name__ == "__main__":
    hard_reset()