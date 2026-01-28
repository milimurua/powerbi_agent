import google.generativeai as genai  # pyright: ignore[reportMissingImports]
from domain.repositories.analytics_repository import AnalyticsRepository
from infrastructure.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiClient(AnalyticsRepository):

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def run_query(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
