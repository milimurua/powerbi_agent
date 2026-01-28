from google.adk.agents import Agent  # pyright: ignore[reportMissingImports]
from google.adk.models import Gemini  # pyright: ignore[reportMissingImports]

from application.use_cases.answer_question import AnswerQuestionUseCase
from domain.entities.question import Question
from infrastructure.outbound.gemini_client import GeminiClient

def create_agent():
    repository = GeminiClient()
    use_case = AnswerQuestionUseCase(repository)

    def handler(message: str) -> str:
        question = Question(text=message)
        return use_case.execute(question)

    return Agent(
        name="ecommerce-agent",
        model=Gemini(model="gemini-1.5-flash"),
        instructions="You are an ecommerce analytics assistant.",
        handler=handler
    )
