import os
from dotenv import load_dotenv

# Force load before ANY langchain import
load_dotenv()

# Explicitly set for LangChain — belt and suspenders approach
os.environ["LANGCHAIN_TRACING_V2"]  = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"]     = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]     = os.getenv("LANGCHAIN_PROJECT", "devops-autopilot")

from langchain_groq import ChatGroq
from utils.logger import get_logger

log = get_logger("base")

def get_LLM(temperature=0.3):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=temperature
    )