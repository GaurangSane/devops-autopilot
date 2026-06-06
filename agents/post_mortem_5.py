from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import get_LLM
from agents.log_analyzer_1 import analyze_logs
from agents.root_cause_2 import log_root_analyze
from agents.fix_proposer_3 import poposes_fixes
from agents.runbook_writer_4 import write_runbook
from datetime import datetime
import os
from utils.logger import get_logger
from utils.retry import llm_retry

@llm_retry
def _invoke_model(llm,messsages):
    return llm.invoke(messsages)

log = get_logger("post_mortem")

SYSTEM_PROMPT ="""
You are a principal engineer and incident commander with experience writing 
post-mortem reports at companies like Google, Stripe, and PagerDuty.

A post-mortem is a blameless, factual document written AFTER an incident is 
resolved. It is read by engineering leadership, product teams, and sometimes 
customers. It must be:
- Blameless (no finger-pointing at individuals)
- Factual (stick to what the data shows)
- Actionable (every problem must have an owner and deadline)
- Clear to non-technical stakeholders

The post-mortem serves two purposes:
1. Document what happened for future reference
2. Drive concrete improvements so it never happens again

Format your response with these EXACT headers:
- INCIDENT TITLE:
- SEVERITY:
- DATE & DURATION:
- EXECUTIVE SUMMARY: (3-4 sentences, non-technical, suitable for C-suite)
- TIMELINE:
- TECHNICAL SUMMARY:
- IMPACT ANALYSIS:
- ROOT CAUSE:
- WHAT WENT WELL:
- WHAT WENT WRONG:
- ACTION ITEMS: (each must have: Task | Owner Role | Priority | Deadline)
- LESSONS LEARNED:
"""

def write_post_mortem(log_analysis:str,root_cause:str,fixes:str,runbook:str) -> str:
    log.info("started post mortem")
    try:
        model = get_LLM(temperature=0.2)
        combined_context = f"""
        LOG ANALYSIS:
        {log_analysis}

        ROOT CAUSE ANALYSIS:
        {root_cause}

        PROPOSED FIXES:
        {fixes}

        RUNBOOK CREATED:
        {runbook}
        Incident date : {datetime.now().strftime("%Y-%m-%d")}
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
        Write a complete blameless post-mortem report for this incident.
        The executive summary must be readable by a non-technical CEO.
        Action items must be specific with owner roles and deadlines.
        Timeline must be chronological with exact timestamps from the logs.
        Action items table MUST have minimum 5 rows.
        Timeline MUST use exact timestamps from the logs.
        Executive summary MUST be understandable by a non-technical reader.
        {combined_context}
        """)
            ]

        response = _invoke_model(model,messsages=messages)
        log.info('completed Post portem')
        return response.content
    except Exception as e:
        log.info(f"post mortem failed")
        raise

def save_post_mortem(post_mortem:str,filename:str=None)->str:
    os.makedirs("post_mortems",exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_mortems/post_mortem__{timestamp}.md"

    with open(filename,"w") as f:
        f.write(post_mortem)

    return filename


if __name__ == "__main__":
    with open("tests/sample_logs.txt","r") as f:
        logs = f.read()

    log_analysis = analyze_logs(logs=logs)
    root_cause = log_root_analyze(log_analysis=log_analysis)
    fixes = poposes_fixes(root_cause=root_cause)
    runbook = write_runbook(log_analysis,root_cause,fixes["fixes"])
    post_mortem_1 = write_post_mortem(log_analysis,root_cause,fixes['fixes'],runbook)
    saved_path = save_post_mortem(post_mortem_1)
    print(saved_path)    



