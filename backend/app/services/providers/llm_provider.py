
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

def get_llm(model_name: str, temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    """
    Initializes and returns a ChatGoogleGenerativeAI instance.
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=settings.google_api_key,
        convert_system_message_to_human=True,
        response_mime_type="application/json",
    )
