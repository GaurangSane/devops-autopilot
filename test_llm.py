from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load your .env file
load_dotenv()

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3  # Lower = more focused, less creative (good for analysis tasks)
)

# Test call
response = llm.invoke("Say hello and tell me what you are in one sentence.")
print(response.content)
print(os.getenv("GEMINI_API_KEY"))  # Should print your key, not None