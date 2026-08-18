import json
from google import genai
from app.schemas.contracts import Situation
from app.core.config import settings
from app.ai.intelligence.prompts import SITUATION_EXTRACTION_PROMPT

class SituationParser:
    def __init__(self):
        # We mock this for unit tests or configure a dummy client if keys aren't set
        self.api_key = settings.gemini_api_key or "DUMMY_KEY"
        self.model = "gemini-3.6-flash"

    def parse(self, user_input: str) -> Situation:
        if self.api_key == "DUMMY_KEY" or "MOCK" in user_input:
            # Fallback for unit testing without API calls
            return Situation(
                category="Mock Category",
                subcategory="Mock Subcategory",
                facts=[user_input],
                parties=[]
            )
            
        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=[
                    SITUATION_EXTRACTION_PROMPT,
                    f"User Input: {user_input}"
                ],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Situation,
                    temperature=0.1
                )
            )
            
            if hasattr(response, "parsed") and response.parsed:
                 return response.parsed
            
            # Fallback if raw text
            data = json.loads(response.text)
            return Situation(**data)
        except Exception as e:
            raise RuntimeError(f"Failed to parse situation via Gemini: {str(e)}")
