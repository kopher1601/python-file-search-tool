import os

from dotenv.main import load_dotenv
from google import genai

load_dotenv()

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set",
            "Please set the GEMINI_API_KEY environment variable in your .env file",
        )
    return genai.Client(api_key=api_key)