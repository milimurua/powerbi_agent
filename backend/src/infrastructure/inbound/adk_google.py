from google.adk.agents import LlmAgent  # pyright: ignore
from google.adk.models import Gemini  # pyright: ignore

from infrastructure.inbound.tools.answer_question_tool import answer_question  # pyright: ignore[reportMissingImports]

def create_agent():
    return LlmAgent(
        name="powerbi_agent",
        model=Gemini(model="gemini-2.5-flash"),
        tools=[answer_question]
    )
