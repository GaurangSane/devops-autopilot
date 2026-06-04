from langchain_core.messages import HumanMessage,SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from agents.base import get_LLM
from agents.log_analyzer_1 import analyze_logs
from agents.root_cause_2 import log_root_analyze
from dotenv import load_dotenv
import os

load_dotenv()

search_tool = TavilySearchResults(
    max_results=3,
    tavily_api_key = os.getenv("TAVILY_API_KEY")
)

SYSTEM_PROMPT = """
You are a senior DevOps engineer and solutions architect with deep expertise 
in distributed systems, databases, and production incident resolution.
You MUST reference the search results. Quote specific configs found online.

You will receive:
1. A root cause analysis of a production incident
2. Real search results with relevant solutions and documentation

Your job is to propose CONCRETE, ACTIONABLE fixes — not generic advice.
Every fix must include:
- Exact commands, config changes, or code snippets where applicable
- Priority (Immediate / Short-term / Long-term)
- Estimated time to implement
- Risk level of applying the fix (Low / Medium / High)

Format your response with these exact headers:
- IMMEDIATE FIXES: (apply right now to restore service)
- SHORT-TERM FIXES: (apply within 1 week to prevent recurrence)
- LONG-TERM FIXES: (architectural improvements for next quarter)
- IMPLEMENTATION RISKS:
"""

def get_search_queries(root_cause : str) -> list[str]:
    model = get_LLM(temperature=0.2)
    message = [
        SystemMessage(content="""
        You are a DevOps expert. 
        Given a root cause analysis, generate exactly 3 specific search queries
        to find solutions. Return ONLY the 3 queries, one per line, nothing else.
        Make queries specific and technical — include technology names, error types.
        """),
        HumanMessage(content=f"Generate 3 search queries for this RCA:\n\n{root_cause}")
    ]

    response = model.invoke(message)
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return queries[:3]

def search_web(queries:list[str]) -> str:
    all_search = []
    for query in queries:
        try:
            result = search_tool.invoke(query)
            for r in result:
                all_search.append(f"source: {r['url']}\n, Content: {r['content']}\n")
        except Exception as e:
            print(f"Search failed for {query}\n : {e}\n")
            continue

    return "...\n\n".join(all_search)     

def poposes_fixes(root_cause: str) -> dict:
    model = get_LLM(temperature=0.2)

    queries = get_search_queries(root_cause=root_cause)
    searched_queries = search_web(queries=queries)

    message = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
    Root Cause Analysis:
    {root_cause}

    Real Solutions Found Online:
    {searched_queries}

    Based on both the root cause and the real solutions above,
    propose concrete fixes with exact commands and configurations.
    """)
    ]

    response = model.invoke(message)
    return {
        "queries":queries,
        "search_results" : searched_queries,
        "fixes" : response.content
    }





if __name__ == "__main__":
    with open("tests/sample_logs.txt","r") as f:
        log = f.read()

    log_analysis1 = analyze_logs(logs=log)

    root_cause1 = log_root_analyze(log_analysis=log_analysis1)

    result = poposes_fixes(root_cause=root_cause1)
    for q in result["queries"]:
        print(f"{q}\n")
    print(result["fixes"])              

    
    


