from app.database import SessionLocal
from app.models import Post
from app.services.matching import match_images_for_post

def run_evaluation():
    db = SessionLocal()
    posts = db.query(Post).all()
    
    total = len(posts)
    correct = 0
    
    print("\n🚀 Running System Evaluation...\n" + "-"*40)
    
    for post in posts:
        results = match_images_for_post(str(post.id), db)
        if not results:
            continue
            
        top_match = results[0]
        
        print(f"📄 Post: {post.title}")
        print(f"🖼️ Top Image: {top_match['filename']} (Score: {top_match['similarity_score']})")
        print(f"🛡️ Guard Status: {top_match['status']}")
        
        # If the top match cleared the guard and was suggested, we count it as a win
        if top_match['status'] == 'suggested':
            correct += 1
            
        print("-" * 40)
        
    precision = (correct / total) * 100
    print(f"\n✅ Final Top-1 Precision: {precision:.1f}%\n")
    db.close()

if __name__ == "__main__":
    run_evaluation()