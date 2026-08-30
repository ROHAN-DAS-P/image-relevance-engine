from app.database import SessionLocal, init_db
from app.models import Post, AICostLog
from app.services.embedding import generate_embedding

POSTS_DATA = [
    {
        "title": "The Elusive Red Fox: Behavior and Forest Habitat",
        "content": "A comprehensive study on the red fox (Vulpes vulpes), exploring its hunting techniques, orange coat adaptations, and nocturnal behavior in dense woodland."
    },
    {
        "title": "Winter Pack Dynamics of Eurasian Gray Wolves",
        "content": "Observing gray wolves as they hunt in coordinated packs across frozen tundras and alpine forests during harsh winters."
    },
    {
        "title": "A Guide to Domestic Dog Training",
        "content": "Effective techniques for training puppies and adult domestic dogs in suburban home environments."
    },
    {
        "title": "Modern Cloud Computing Architectures",
        "content": "An overview of microservices, serverless computing, and distributed database systems in large scale SaaS platforms."
    }
]

def seed_posts():
    init_db()
    db = SessionLocal()
    print("Seeding blog posts and generating text embeddings...")

    for item in POSTS_DATA:
        existing = db.query(Post).filter_by(title=item["title"]).first()
        if not existing:
            # Generate embedding for title + content
            text_to_embed = f"{item['title']} {item['content']}"
            result = generate_embedding(text_to_embed)
            
            post = Post(
                title=item["title"],
                content=item["content"],
                embedding=result["vector"]
            )
            db.add(post)
            db.commit()
            
            # Log embedding cost
            db.add(AICostLog(
                job_type="embedding",
                model="text-embedding-004",
                tokens_used=result["tokens"],
                estimated_cost=result["cost"],
                post_id=post.id
            ))
            db.commit()
            print(f"✅ Added & embedded post: '{item['title']}'")

    db.close()
    print("Post seeding complete!")

if __name__ == "__main__":
    seed_posts()