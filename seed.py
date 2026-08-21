import os
import requests
from app.database import SessionLocal, init_db
from app.models import Image

# Using Wikimedia images, which are guaranteed not to 404
IMAGE_DATA = [
    {"filename": "red_fox.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Fox_-_British_Wildlife_Centre_%2817429406401%29.jpg/800px-Fox_-_British_Wildlife_Centre_%2817429406401%29.jpg"},
    {"filename": "gray_wolf.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Eurasian_wolf_2.jpg/800px-Eurasian_wolf_2.jpg"},
    {"filename": "domestic_dog.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collared_Brown_and_White_Dog.jpg/800px-Collared_Brown_and_White_Dog.jpg"},
    {"filename": "brown_bear.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/2010-kodiak-bear-1.jpg/800px-2010-kodiak-bear-1.jpg"},
    {"filename": "red_deer.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Red_deer_stag_2009_denmark.jpg/800px-Red_deer_stag_2009_denmark.jpg"}
]

def seed_images():
    os.makedirs("static/images", exist_ok=True)
    init_db()
    db = SessionLocal()

    print("Downloading images and seeding database...")
    
    # Using the standard Chrome browser header to bypass Wikimedia's 403 bot-blocker
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for data in IMAGE_DATA:
        filepath = os.path.join("static/images", data["filename"])
        
        # Only download if we don't already have it
        if not os.path.exists(filepath):
            print(f"Downloading {data['filename']}...")
            response = requests.get(data["url"], headers=headers, timeout=15)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
            else:
                print(f"Failed to download {data['filename']} - Status Code: {response.status_code}")
        
        # Add to database if not already there
        existing = db.query(Image).filter_by(filename=data["filename"]).first()
        if not existing:
            new_image = Image(filename=data["filename"], status="pending")
            db.add(new_image)
            print(f"Added {data['filename']} to DB.")
    
    db.commit()
    db.close()
    print("✅ Seeding complete!")

if __name__ == "__main__":
    seed_images()