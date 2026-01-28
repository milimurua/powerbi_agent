import os
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

settings = Settings()
