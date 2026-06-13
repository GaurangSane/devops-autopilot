import os
from github import Github
from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import get_LLM
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
log = get_logger("github_agent")

SYSTEM_PROMPT = """
You are a senior software engineer performing codebase analysis
during a production incident.

You have been given:
1. A root cause analysis of the incident
2. Actual source code files from the affected repository

Your job is to:
- Find the EXACT lines of code responsible for or related to the incident
- Explain what the code is doing wrong
- Provide the exact fix with corrected code
- Reference specific file names and line numbers

Be extremely specific. "Change line 47 in payment_service.py" not 
"change your connection pool configuration".

Format response with these exact headers:
- RELEVANT FILES FOUND:
- PROBLEMATIC CODE:
- EXACT FIX:
- ADDITIONAL CODE ISSUES:
"""


def fetch_repo_context(
    repo_url: str,
    affected_services: list,
    root_cause: str
) -> dict:
    """
    Fetches relevant source files from a GitHub repo.
    Smart fetching — only pulls files likely related to the incident.

    Args:
        repo_url: Full GitHub URL e.g. https://github.com/user/repo
        affected_services: List of services from log analysis
        root_cause: Root cause text to guide file selection

    Returns:
        dict with fetched files and their content
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set in .env")

    try:
        g = Github(token)

        # Parse repo path from URL
        # handles: https://github.com/user/repo or github.com/user/repo
        repo_path = repo_url.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
        log.info(f"Fetching repo: {repo_path}")

        repo = g.get_repo(repo_path)

        # Build smart search terms from affected services + root cause
        search_terms = []
        for service in affected_services:
            # payment-service → payment, service
            parts = service.replace("-", "_").replace(" ", "_").split("_")
            search_terms.extend(parts)

        # Add terms from root cause
        important_words = [
            "connection", "pool", "database", "timeout",
            "retry", "circuit", "breaker", "config"
        ]
        for word in important_words:
            if word.lower() in root_cause.lower():
                search_terms.append(word)

        search_terms = list(set(search_terms))  # deduplicate
        log.info(f"Searching for terms: {search_terms}")

        # Fetch repo file tree
        contents = repo.get_contents("")
        all_files = []

        # Recursively get all files (max depth 3 to avoid huge repos)
        def get_files(contents, depth=0):
            if depth > 3:
                return
            for item in contents:
                if item.type == "dir":
                    try:
                        get_files(repo.get_contents(item.path), depth + 1)
                    except:
                        continue
                else:
                    all_files.append(item)

        get_files(contents)

        # Filter to relevant files only
        relevant_extensions = [
            ".py", ".js", ".ts", ".java", ".go",
            ".yaml", ".yml", ".json", ".env.example",
            ".properties", ".conf", ".config"
        ]

        relevant_files = []
        for f in all_files:
            # Skip test files, node_modules, etc
            skip_patterns = [
                "node_modules", "__pycache__", ".git",
                "test_", "_test", ".min.js", "dist/"
            ]
            if any(p in f.path for p in skip_patterns):
                continue

            # Check extension
            if not any(f.path.endswith(ext) for ext in relevant_extensions):
                continue

            # Check if filename matches our search terms
            fname_lower = f.path.lower()
            if any(term.lower() in fname_lower for term in search_terms):
                relevant_files.append(f)

        log.info(f"Found {len(relevant_files)} relevant files")

        # Fetch content of relevant files (max 10 files, max 200 lines each)
        fetched = {}
        for f in relevant_files[:10]:
            try:
                content = f.decoded_content.decode("utf-8")
                # Truncate very large files
                lines = content.split("\n")
                if len(lines) > 200:
                    content = "\n".join(lines[:200]) + "\n... (truncated)"
                fetched[f.path] = content
                log.info(f"  Fetched: {f.path} ({len(lines)} lines)")
            except Exception as e:
                log.warning(f"  Could not decode {f.path}: {e}")
                continue

        return {
            "repo": repo_path,
            "files_found": len(all_files),
            "relevant_files": list(fetched.keys()),
            "file_contents": fetched
        }

    except Exception as e:
        log.error(f"GitHub fetch failed: {e}")
        raise


def analyze_with_github(
    root_cause: str,
    affected_services: list,
    repo_url: str,
    user_context: str = ""
) -> dict:
    """
    Main function — fetches repo context and generates
    codebase-aware fix recommendations.

    Args:
        root_cause: Agent 2 output
        affected_services: From Agent 1 output
        repo_url: GitHub repo URL from user
        user_context: Optional user-provided hypothesis

    Returns:
        dict with repo_data and code_analysis
    """
    llm = get_LLM(temperature=0.1)

    # Step 1: Fetch relevant files
    log.info(f"Starting GitHub analysis for {repo_url}")
    repo_data = fetch_repo_context(repo_url, affected_services, root_cause)

    if not repo_data["file_contents"]:
        log.warning("No relevant files found in repo")
        return {
            "repo_data": repo_data,
            "code_analysis": "No relevant source files found matching the affected services.",
            "github_used": False
        }

    # Step 2: Build context string from files
    code_context = ""
    for filepath, content in repo_data["file_contents"].items():
        code_context += f"\n\n{'='*50}\nFILE: {filepath}\n{'='*50}\n{content}"

    # Step 3: Generate codebase-aware analysis
    user_context_section = ""
    if user_context.strip():
        user_context_section = f"""
ENGINEER'S HYPOTHESIS:
{user_context}
(Take this into account when analyzing the code)
"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
ROOT CAUSE ANALYSIS:
{root_cause}

{user_context_section}

SOURCE CODE FROM REPOSITORY ({repo_data['repo']}):
{code_context}

Find the exact problematic code and provide specific line-level fixes.
""")
    ]

    response = llm.invoke(messages)
    log.info("GitHub code analysis complete")

    return {
        "repo_data": repo_data,
        "code_analysis": response.content,
        "github_used": True
    }


if __name__ == "__main__":
    # Test with a public repo
    from agents.log_analyzer_1 import analyze_logs
    from agents.root_cause_2 import analyze_root_cause

    with open("tests/sample_logs.txt", "r") as f:
        logs = f.read()

    log_analysis  = analyze_logs(logs)
    root_cause    = analyze_root_cause(log_analysis)

    # Test with any public GitHub repo
    result = analyze_with_github(
        root_cause=root_cause,
        affected_services=["payment-service"],
        repo_url="https://github.com/YOUR_USERNAME/YOUR_REPO",
        user_context="We deployed a new version 10 minutes before this error appeared"
    )

    print("\n" + "="*60)
    print("GITHUB AGENT OUTPUT")
    print("="*60)
    print(f"Repo: {result['repo_data']['repo']}")
    print(f"Files scanned: {result['repo_data']['files_found']}")
    print(f"Relevant files: {result['repo_data']['relevant_files']}")
    print("\nCODE ANALYSIS:")
    print(result["code_analysis"])