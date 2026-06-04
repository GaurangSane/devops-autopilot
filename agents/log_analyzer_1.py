from langchain_core.messages import HumanMessage, SystemMessage
from .base import get_LLM

SYSTEM_PROMPT = """
You are an expert DevOps engineer and SRE (Site Reliability Engineer) 
with 10+ years of experience analyzing production incidents.

Your job is to analyze raw logs and extract:
1. WHAT broke (which services/components failed)
2. WHEN it started (first sign of trouble)
3. SEVERITY (Critical / High / Medium / Low)
4. ERROR PATTERNS (what types of errors are repeating)
5. AFFECTED SERVICES (list every service mentioned)

Be specific, technical, and concise.
Format your response with clear sections using these exact headers:
- WHAT BROKE:
- WHEN IT STARTED:
- SEVERITY:
- ERROR PATTERNS:
- AFFECTED SERVICES:
"""

def analyze_logs(logs : str) ->str:
    model = get_LLM(temperature=0.1)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"analyze the log : \n\n {logs}")
    ]

    response = model.invoke(messages)
    return response.content

if __name__ == "__main__":
    with open("tests/sample_logs.txt","r") as f:
        logs = f.read()
    result = analyze_logs(logs=logs)
    print(result)


