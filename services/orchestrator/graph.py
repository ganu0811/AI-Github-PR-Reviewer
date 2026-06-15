import json
import operator
import re
from typing import TypedDict, Annotated

from langfuse.openai import OpenAI   # langfuse will be used for LLM tracing
from langgraph.graph import StateGraph, END
from langgraph.constants import Send

client = OpenAI()

PROMPTS = {
    "static_analysis": "You are a static analysis tool. Review this git diff for code complexity issues, unused variables, , and poor naming. Return only a JSON array. Each item must have keys: file, line, severity (info/warning/error), message.",
    "security": "You are a security scanner. Review this git diff for OWASP Top 10 vulnerabilities, hardcoded secrets, and SQL injection risks. Return only a JSON array. Each item must have keys: file, line, severity, message.",
    "architecture": "You are an architecture reviewer. Review this git diff for separation of concerns violations, missing error handling, and improper dependency usage. Return only a JSON array. Each item must have keys: file, line, severity, message."
}

'''The function will convert JSON response into a structured format'''

def parse_json_response(raw: str) -> list:
    raw = raw.strip()
    match = re.search(r"```(?json)?\s*([\s\S]*?)```", raw)
    if match:
        raw = match.group(1).strip()
    try:
        return json.loads(raw)
    except Exception:
        return []


'''Graphstate defines the flow between the node'''
class GraphState(TypedDict):
    diff: str                   # diff variable is the git difference
    patterns: list[str]         # patterns is coming from the learner service
    findings: Annotated[list[dict], operator.add]
    

def make_node(agent_name:str, get_prompt):
    def node(state: GraphState) -> dict:
        prompt = get_prompt(state) if callable(get_prompt) else get_prompt
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": state["diff"]},
            ]
        )
        items = parse_json_response(response.choices[0].message.content)
        for item in items:
            item["agent"] = agent_name
        return {"findings": items}
    return node 

def _style_prompt(state: GraphState) -> str:
    patterns_str = "\n".join(state["patterns"]) if state["patterns"] else "None"
    return f"You are a code style reviewer. Review this git diff for formatting, readability, and consistency issues. Common patterns this team has had before: {patterns_str}. Return only a JSON array. Each item must have keys: file, line, severity, message."


'''Merge_node follows the concept of Deduplication. E.g, Agent1 and Agent2 can give same error twice.
So to deal with multiple errors deduplication is used'''

def merge_node(state: GraphState) -> dict:
    seen = set()
    merged = []
    for finding in state["findings"]:
        key = (finding.get("file"), finding.get("line"), finding.get("agent"), finding.get("message"))
        if key not in seen:
            seen.add(key)
            merged.append(finding)
    return {"findings": merged}



'''All the four agents are running in parallel at the same time'''
def fan_out(state: GraphState):
    return [
        Send("static_analysis", state),
        Send("security", state),
        Send("style", state),
        Send("architecture", state)
        
    ]

def build_graph() -> StateGraph:
    builder = StateGraph(GraphState)
    
    builder.add_node("static_analysis", make_node("static_analysis", PROMPTS["static_analysis"]))
    builder.add_node("security", make_node("security", PROMPTS["security"]))
    builder.add_node("style", make_node("style", _style_prompt))
    builder.add_node("architecture",make_node("architecture", PROMPTS["architecture"]))
    builder.add_node("merge",merge_node)
    
    builder.set_conditional_entry_point(fan_out)  # Instead of starting with one node, it starts by splitting into multiple node, running all the 4 agents in parallel.
    
    for name in ("static_analysis", "security", "style", "architecture"):
        builder.add_edge(name, "merge")
    builder.add_edge("merge", END)
    
    return builder.compile()
        
    