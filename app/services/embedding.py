# #import google.generativeai as genai
# from app.config import settings
# from google import genai
# from google.genai import types

# genai.configure(api_key=settings.GEMINI_API_KEY)

# def generate_embedding(text: str) -> dict:
#     """
#     Generates a 768-dimensional embedding vector for a given text
#     using Gemini's text-embedding-004 model.
#     """
#     response = genai.embed_content(
#         model="models/gemini-embedding-001",
#         content=text,
#         task_type="SEMANTIC_SIMILARITY"
#     )
    
#     vector = response['embedding']
    
#     # Rough estimate of tokens and cost for embedding calls
#     token_count = len(text.split()) * 2
#     estimated_cost = (token_count * 0.02) / 1_000_000 # Free tier, tracked for audit
    
#     return {
#         "vector": vector,
#         "tokens": token_count,
#         "cost": estimated_cost
#     }

from app.config import settings
from google import genai
from google.genai import types


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_embedding(text: str) -> dict:
    """
    Generates a 768-dimensional embedding vector for a given text
    using Gemini's gemini-embedding-001 model.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=768,
        ),
    )

    vector = response.embeddings[0].values

    # Rough estimate of tokens and cost for embedding calls
    token_count = len(text.split()) * 2
    estimated_cost = (token_count * 0.02) / 1_000_000

    return {
        "vector": vector,
        "tokens": token_count,
        "cost": estimated_cost,
    }