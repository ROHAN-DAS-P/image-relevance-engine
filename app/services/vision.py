import google.generativeai as genai
from pydantic import BaseModel, Field
import typing_extensions as typing
from app.config import settings

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# 1. Define the exact JSON shape we want the AI to return
class ImageTags(BaseModel):
    subject: str = Field(description="The primary subject of the image (e.g., 'red fox', 'gray wolf')")
    category: str = Field(description="The broad category (e.g., 'animal', 'landscape')")
    attributes: list[str] = Field(description="A list of 3-5 visual attributes (e.g., 'orange fur', 'wild')")
    caption: str = Field(description="A short descriptive caption of what is happening in the image")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 of this classification")

def analyze_image_with_gemini(file_path: str) -> dict:
    import PIL.Image
    
    # Load the local image
    img = PIL.Image.open(file_path)
    
    # We use Flash because it's insanely fast and has a free tier
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 2. Ask for the tags and strictly enforce our Pydantic schema
    response = model.generate_content(
        ["Analyze this image and extract the metadata.", img],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ImageTags,
            temperature=0.1 # Low temperature for more deterministic tags
        )
    )
    
    # 3. Extract the usage for cost tracking (Layer 3 Requirement)
    prompt_tokens = response.usage_metadata.prompt_token_count
    completion_tokens = response.usage_metadata.candidates_token_count
    
    # Gemini 1.5 Flash rough pricing per 1M tokens (Free tier is $0, but we track value)
    cost = (prompt_tokens * 0.075 / 1_000_000) + (completion_tokens * 0.30 / 1_000_000)
    
    # Parse the guaranteed JSON text back into a dictionary
    import json
    metadata = json.loads(response.text)
    
    return {
        "metadata": metadata,
        "tokens": prompt_tokens + completion_tokens,
        "cost": cost
    }