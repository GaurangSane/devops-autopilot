import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "devops-autopilot")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")

print("Tracing:", os.environ["LANGCHAIN_TRACING_V2"])
print("Project:", os.environ["LANGCHAIN_PROJECT"])
print("Key set:", bool(os.environ["LANGCHAIN_API_KEY"]))

# Now make a real LLM call — this MUST appear in LangSmith
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

print("\nMaking test LLM call...")
response = llm.invoke([HumanMessage(content="Say: TRACE TEST SUCCESSFUL")])
print("Response:", response.content)
print("\n✅ Done — check LangSmith dashboard now")
print("URL: https://smith.langchain.com")