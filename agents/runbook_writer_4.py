from langchain_core.messages import HumanMessage,SystemMessage
from agents.base import get_LLM
from datetime import datetime
from agents.log_analyzer_1 import analyze_logs
from agents.root_cause_2 import log_root_analyze
from agents.fix_proposer_3 import poposes_fixes
from utils.logger import get_logger
from utils.retry import llm_retry

@llm_retry
def _invoke_model(llm,messsages):
    return llm.invoke(messsages)

log = get_logger("runbook_writer")

SYSTEM_PROMPT = """
You are a senior SRE technical writer with 10+ years of experience writing 
production runbooks for companies like Google, Netflix, and Stripe.

A runbook is a step-by-step operational guide that ANY engineer — even someone 
unfamiliar with the system — can follow at 2am during an incident to diagnose 
and resolve issues quickly.

Golden rules of runbooks:
- Steps must be numbered and sequential
- Every step must have an expected outcome
- Include exact commands, not descriptions of commands
- Include decision points (IF this THEN that)
- Include escalation paths (when to wake someone up)
- Include rollback steps if a fix makes things worse
- Write for someone who is stressed, tired, and unfamiliar with the system

Format your response with these EXACT headers:
- RUNBOOK TITLE:
- INCIDENT SUMMARY:
- PREREQUISITES:
- DETECTION STEPS:
- DIAGNOSIS STEPS:
- RESOLUTION STEPS:
- VERIFICATION STEPS:
- ROLLBACK PLAN:
- ESCALATION PATH:
- PREVENTION CHECKLIST:
"""

def write_runbook(log_analysis:str,root_cause:str,fixes:str) ->str:
    log.info("Started runbook writer")
    try:
        model = get_LLM(temperature=0.2)
        combined_context = f"""
            INCIDENT LOG ANALYSIS:
        {log_analysis}

        ROOT CAUSE ANALYSIS:
        {root_cause}

        PROPOSED FIXES:
        {fixes}
        todays date = {datetime.now().strftime("%Y-%m-%d")}
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
        Write a complete production runbook based on this incident analysis.
        Make it detailed enough that a junior engineer can follow it alone at 2am.
        {combined_context}
        """)
        ]

        response = _invoke_model(model,messsages=messages)
        log.info("run book completed.")
        return response.content
    except Exception as e:
        log.error(f"runbook writer failed")
def save_runbook(runbook:str,filename:str=None) -> str:
    import os
    os.makedirs("runbook",exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"runbook/runbook_{timestamp}.md"

    with open(filename,"w") as f:
        f.write(runbook)  

    return filename

if __name__ == "__main__":
    with open("tests/sample_logs.txt","r") as f:
        logs = f.read()
    log_analysis = analyze_logs(logs)
    root_analysis = log_root_analyze(log_analysis=log_analysis)
    fixes = poposes_fixes(root_cause=root_analysis)
    runbook = write_runbook(log_analysis,root_analysis,fixes["fixes"])
    print(runbook)
    saved_path = save_runbook(runbook=runbook)
    print(saved_path)      
