import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-ultra-550b-a55b:free")

def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Factory function to get a standardized LLM client across all agents."""
    return ChatOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        model=MODEL_NAME,
        temperature=temperature,
        # Passed explicitly to satisfy LangChain's updated requirements
        extra_body={
            "reasoning": {"enabled": True}
        }
    )