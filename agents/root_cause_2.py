from langchain_core.messages import HumanMessage , SystemMessage
from .base import get_LLM
from agents.log_analyzer_1 import analyze_logs
from utils.logger import get_logger
from utils.retry import llm_retry

@llm_retry
def _invoke_model(llm,messsages):
    return llm.invoke(messsages)

log = get_logger("root_analysis")

SYSTEM_PROMPT = """
You are a senior Site Reliability Engineer specializing in distributed systems 
and root cause analysis (RCA).

You will receive a structured log analysis from another engineer.
Your job is to determine the ROOT CAUSE of the incident — not just what broke,
but WHY it broke and how one failure cascaded into others.

Think in terms of:
- Primary root cause (the single origin of the failure)
- Cascade chain (how failure spread from service to service)
- Contributing factors (what made the system vulnerable)
- What DIDN'T fail and why (important for understanding system resilience)

Format your response with these exact headers:
- PRIMARY ROOT CAUSE:
- CASCADE CHAIN:
- CONTRIBUTING FACTORS:
- RESILIENCE OBSERVATIONS:
- CONFIDENCE LEVEL: (High / Medium / Low — how confident are you in this RCA)
Do NOT repeat the log analysis. Go deeper. Find the origin.
"""

def log_root_analyze(log_analysis : str) -> str:
    log.info("Starting root analysis", )
    try:
        model = get_LLM(temperature=0.2)
        message = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Based on log analysis help to determine root causea: \n\n{log_analysis} ")
        ]

        response = _invoke_model(model,messsages=message)
        log.info("root analysis completed successfully")
        return response.content

    except Exception as e:
         log.error(f"root analysis failed: {e}")
         raise

if __name__ == "__main__":
    with open("tests/sample_logs.txt","r") as f:
        logs = f.read()

    log_analysis = analyze_logs(logs=logs)

    result = log_root_analyze(log_analysis=log_analysis)
    print(result)

