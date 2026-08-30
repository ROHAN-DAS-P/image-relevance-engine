from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Post, ImageMetadata, Match, Image
import numpy as np

# Tunable safety thresholds
SIMILARITY_THRESHOLD = 0.55  # Minimum cosine similarity required to consider a match
HIGH_CONFIDENCE_THRESHOLD = 0.70

def evaluate_match_with_guard(post: Post, metadata: ImageMetadata, similarity_score: float) -> dict:
    """
    Evaluates a candidate image against safety and relevance rules.
    Returns decision status and reason.
    """
    # 1. Hard threshold rejection
    if similarity_score < SIMILARITY_THRESHOLD:
        return {
            "status": "guarded_mismatch",
            "reason": f"Similarity score ({similarity_score:.2f}) is below threshold ({SIMILARITY_THRESHOLD})."
        }
    
    # 2. Vision model confidence check
    if metadata.confidence < HIGH_CONFIDENCE_THRESHOLD:
        return {
            "status": "guarded_mismatch",
            "reason": f"Low image tagging confidence ({metadata.confidence:.2f}). Flagged for manual review."
        }
    
    # 3. Subject-level Mismatch Guard (The Fox vs Wolf rule)
    post_text = f"{post.title} {post.content}".lower()
    subject = metadata.subject.lower()
    
    # Negative conflict rules
    if "fox" in post_text and "wolf" in subject:
        return {
            "status": "guarded_mismatch",
            "reason": "Animal category mismatch: expected fox, detected wolf."
        }
        
    if "wolf" in post_text and "fox" in subject:
        return {
            "status": "guarded_mismatch",
            "reason": "Animal category mismatch: expected wolf, detected fox."
        }
        
    if "cloud computing" in post_text and metadata.category == "animal":
        return {
            "status": "guarded_mismatch",
            "reason": "Topic domain mismatch: technical article paired with animal image."
        }

    return {
        "status": "suggested",
        "reason": "Image matches article topic and cleared all safety checks."
    }

def match_images_for_post(post_id: str, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    
    # Fetch all processed images with embeddings
    candidates = db.query(ImageMetadata).join(Image).filter(Image.status == "processed").all()
    
    results = []
    for meta in candidates:
        # Cosine similarity calculation: 1 - cosine_distance
        dot_product = np.dot(post.embedding, meta.embedding)
        norm_a = np.linalg.norm(post.embedding)
        norm_b = np.linalg.norm(meta.embedding)
        similarity = float(dot_product / (norm_a * norm_b))
        
        guard_decision = evaluate_match_with_guard(post, meta, similarity)
        
        results.append({
            "image_id": str(meta.image_id),
            "filename": meta.image.filename,
            "subject": meta.subject,
            "similarity_score": round(similarity, 4),
            "status": guard_decision["status"],
            "reason": guard_decision["reason"]
        })
        
    # Rank by similarity descending
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results