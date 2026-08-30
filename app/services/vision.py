from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.config import settings


# Initialize Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)


# Define the exact JSON shape we want the AI to return
class ImageTags(BaseModel):
    subject: str = Field(
        description="The primary subject of the image (e.g., 'red fox', 'gray wolf')"
    )
    category: str = Field(
        description="The broad category (e.g., 'animal', 'landscape')"
    )
    attributes: list[str] = Field(
        description="A list of 3-5 visual attributes (e.g., 'orange fur', 'wild')"
    )
    caption: str = Field(
        description="A short descriptive caption of what is happening in the image"
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0 of this classification"
    )


def analyze_image_with_gemini(file_path: str) -> dict:
    import json
    import PIL.Image

    # Load the local image
    img = PIL.Image.open(file_path)

    # Generate structured metadata using Gemini
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            "Analyze this image and extract the metadata.",
            img,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ImageTags,
            temperature=0.1,
        ),
    )

    # Extract usage for cost tracking
    prompt_tokens = response.usage_metadata.prompt_token_count
    completion_tokens = response.usage_metadata.candidates_token_count

    # Rough estimated value for tracking
    cost = (
        prompt_tokens * 0.075 / 1_000_000
        + completion_tokens * 0.30 / 1_000_000
    )

    # Parse the structured JSON response
    metadata = json.loads(response.text)

    return {
        "metadata": metadata,
        "tokens": prompt_tokens + completion_tokens,
        "cost": cost,
    }