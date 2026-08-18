from google import genai
from typing import List
from app.core.config import settings

class GeminiEmbedder:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_embedding_model
        self.dimensions = settings.gemini_embedding_dimensions

    def embed_text(self, text: str) -> List[float]:
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
            )
            embedding = response.embeddings[0].values
            
            if len(embedding) != self.dimensions:
                raise ValueError(f"Embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}")
                
            return embedding
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
