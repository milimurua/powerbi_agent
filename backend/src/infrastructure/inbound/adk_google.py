from google.adk.agents import Agent  # pyright: ignore[reportMissingImports]
from google.adk.models import Gemini  # pyright: ignore[reportMissingImports]

from application.use_cases.answer_question import AnswerQuestionUseCase
from domain.entities.question import Question
from infrastructure.outbound.gemini_client import GeminiClient

def create_agent():
    def handler(message: str) -> str:
        try:
            repository = GeminiClient()
            use_case = AnswerQuestionUseCase(repository)
            question = Question(text=message)
            return use_case.execute(question)
        except Exception as e:
            return f"Error: {str(e)}"

    return Agent(
        name="powerbi-agent",
        model=Gemini(model="gemini-1.5-flash"),
        instructions="You are an analytics assistant.",
        handler=handler
    )
