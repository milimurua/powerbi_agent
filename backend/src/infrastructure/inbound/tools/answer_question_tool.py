from domain.entities.question import Question
from infrastructure.outbound.gemini_client import GeminiClient

def answer_question(question_text: str) -> str:
    """
    Answer a question about analytics data.
    
    Args:
        question_text: The question to answer
        
    Returns:
        The answer to the question
    """
    question = Question(text=question_text)
    client = GeminiClient()
    return client.run_query(
        f"You are an analytics assistant.\nUser question: {question.text}"
    )


