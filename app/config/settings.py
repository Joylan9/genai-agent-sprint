import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.50))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 10))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))


settings = Settings()
