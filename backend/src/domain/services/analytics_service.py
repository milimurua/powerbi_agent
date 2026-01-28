class AnalyticsService:
    def build_prompt(self, question:str) -> str:
       return f""" You are an analytics assitant. 
       User question: {question}
       Answer in bussiness language."""
 