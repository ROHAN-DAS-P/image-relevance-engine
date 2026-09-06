from app.database import SessionLocal
from app.models import Post
from app.services.matching import match_images_for_post

# def run_evaluation():
#     db = SessionLocal()
#     posts = db.query(Post).all()
    
#     total = len(posts)
#     correct = 0
    
#     print("\n🚀 Running System Evaluation...\n" + "-"*40)
    
#     for post in posts:
#         results = match_images_for_post(str(post.id), db)
#         if not results:
#             continue
            
#         top_match = results[0]
        
#         print(f"📄 Post: {post.title}")
#         print(f"🖼️ Top Image: {top_match['filename']} (Score: {top_match['similarity_score']})")
#         print(f"🛡️ Guard Status: {top_match['status']}")
        
#         # If the top match cleared the guard and was suggested, we count it as a win
#         if top_match['status'] == 'suggested':
#             correct += 1
            
#         print("-" * 40)
        
#     precision = (correct / total) * 100
#     print(f"\n✅ Final Top-1 Precision: {precision:.1f}%\n")
#     db.close()

# if __name__ == "__main__":
#     run_evaluation()


GROUND_TRUTH = {
    "The Elusive Red Fox: Behavior and Forest Habitat": "red_fox.jpg",
    "Winter Pack Dynamics of Eurasian Gray Wolves": "gray_wolf.jpg",
    "A Guide to Domestic Dog Training": "domestic_dog.jpg",
    "Modern Cloud Computing Architectures": None  # No match should clear the bar
}

def run_evaluation():
    db = SessionLocal()
    posts = db.query(Post).all()
    correct = 0
    total = len(posts)

    for post in posts:
        expected = GROUND_TRUTH.get(post.title)
        results = match_images_for_post(str(post.id), db)
        
        # Valid top candidate that cleared the guard
        valid_candidates = [r for r in results if r["status"] == "suggested"]
        top_suggestion = valid_candidates[0]["filename"] if valid_candidates else None
        
        if top_suggestion == expected:
            correct += 1
            print(f"✅ PASS: '{post.title}' -> Expected: {expected}, Got: {top_suggestion}")
        else:
            print(f"❌ FAIL: '{post.title}' -> Expected: {expected}, Got: {top_suggestion}")

    precision = (correct / total) * 100
    print(f"\nFinal Verified Top-1 Precision: {precision:.1f}%")

if __name__ == "__main__":
    run_evaluation()