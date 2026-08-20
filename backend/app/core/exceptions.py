class QuotaExhaustedError(Exception):
    """Raised when the Gemini API quota is permanently exhausted."""
    def __init__(self, message="AI service is temporarily unavailable because the current usage limit has been reached. Your information has not been lost. Please try again later."):
        self.message = message
        super().__init__(self.message)
