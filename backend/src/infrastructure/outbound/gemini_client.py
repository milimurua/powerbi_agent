import google.generativeai as genai  # pyright: ignore[reportMissingImports]
from domain.repositories.analytics_repository import AnalyticsRepository
from infrastructure.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiClient(AnalyticsRepository):

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Missing GEMINI_API_KEY env var")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def run_query(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
