from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    demo_mode: bool = False
    supabase_url: str = ""
    supabase_service_key: str = ""
    gemini_api_key: str = ""
    gemini_api_key_backup: str = ""
    generation_model: str = "gemini-3.6-flash"
    situation_model: str = "gemini-3.6-flash"
    document_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_embedding_dimensions: int = 768
    
    # Reranker weights
    weight_semantic: float = 0.5
    weight_keyword: float = 0.2
    weight_authority: float = 0.2
    weight_freshness: float = 0.1

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

def validate_config():
    if not settings.gemini_api_key:
        raise ValueError("STARTUP ERROR: GEMINI_API_KEY is required.")
        
    if not settings.demo_mode:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError("STARTUP ERROR: Production mode requires SUPABASE_URL and SUPABASE_SERVICE_KEY. Set DEMO_MODE=true for local execution.")

