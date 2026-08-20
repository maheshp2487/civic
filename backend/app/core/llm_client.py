import time
from typing import Any, List, Optional
from google import genai
from app.core.config import settings
from app.core.exceptions import QuotaExhaustedError

class ConfigurationError(RuntimeError):
    pass

def _is_quota_exhausted(error_msg: str) -> bool:
    error_msg = error_msg.lower()
    return "429" in error_msg and ("quota" in error_msg or "exhausted" in error_msg or "limit" in error_msg)

def _is_transient(error_msg: str) -> bool:
    error_msg = error_msg.lower()
    return "429" in error_msg or "503" in error_msg or "unavailable" in error_msg

def _is_auth_error(error_msg: str) -> bool:
    error_msg = error_msg.lower()
    return "401" in error_msg or "403" in error_msg or "unauthenticated" in error_msg or "permission" in error_msg or "api key not valid" in error_msg

def generate_content_with_fallback(
    model: str,
    contents: List[Any],
    config: Optional[genai.types.GenerateContentConfig] = None,
    mock_input: Optional[str] = None
) -> Any:
    """
    Centralized wrapper for Gemini API calls.
    Implements dual-key fallback logic for quota exhaustion.
    """
    
    # Check for test mocks
    if mock_input and "MOCK_ERROR_429" in mock_input:
        raise QuotaExhaustedError()

    primary_key = settings.gemini_api_key or "DUMMY_KEY"
    backup_key = settings.gemini_api_key_backup
    
    # If Dummy key, we can't do real requests in this centralized place unless the caller handles dummy.
    # The caller will handle dummy logic, this wrapper expects a real key if not returning dummy.
    
    client = genai.Client(api_key=primary_key)
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as e:
            error_msg = str(e)
            
            # 1. Confirmed Quota Exhaustion
            if _is_quota_exhausted(error_msg):
                # Break out of the retry loop to use the backup
                break
                
            # 2. Transient Errors (429 rate limit, 503)
            if _is_transient(error_msg) and attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
                
            # 3. Auth error on primary
            if _is_auth_error(error_msg):
                raise ConfigurationError(f"Primary API key configuration error: {error_msg}")
                
            # 4. Fatal or max retries reached
            raise RuntimeError(f"Generation failed on primary key after {attempt + 1} attempts: {error_msg}")

    # Fallback to backup key if we broke out of the loop due to Quota Exhaustion
    if not backup_key:
        raise QuotaExhaustedError()
        
    backup_client = genai.Client(api_key=backup_key)
    try:
        return backup_client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    except Exception as e:
        error_msg = str(e)
        if _is_quota_exhausted(error_msg):
            raise QuotaExhaustedError()
        if _is_auth_error(error_msg):
            raise ConfigurationError(f"Backup API key configuration error: {error_msg}")
            
        raise RuntimeError(f"Generation failed on backup key: {error_msg}")
