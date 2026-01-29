from domain.entities.question import Question
from domain.services.analytics_service import AnalyticsService
from domain.repositories.analytics_repository import AnalyticsRepository

class AnswerQuestionUseCase:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository
        self.service = AnalyticsService()

    def execute(self, question: Question) -> str:
        prompt = self.service.build_prompt(question.text)
        return self.repository.run_query(prompt)