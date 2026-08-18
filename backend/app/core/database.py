from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_service_key:
        raise ValueError("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
    return create_client(settings.supabase_url, settings.supabase_service_key)

# Optionally instantiate a global client for easy imports if needed:
# supabase_db = get_supabase_client()
