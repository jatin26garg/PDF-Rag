import re
import json

from langchain_ollama import ChatOllama
from app.config import settings
from app.agent.state import AgentState
from app.agent.tools import rag_search,write_output

from datetime import datetime


_llm = ChatOllama(model= settings.CHAT_MODEL ,
                  base_url=settings.OLLAMA_BASE_URL,
                  temperature=0.2,
                  format= 'json'
                  )


def _clean_json(raw: str) -> str:
    """
    qwen3 emits <think>...</think> reasoning before its actual answer.
    Strip that out, then pull the first {...} or [...] block so json.loads
    doesn't choke on stray reasoning text or markdown fences.
    """
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    match = re.search(r"(\{.*\}|\[.*\])", raw, flags=re.DOTALL)
    return match.group(1) if match else raw

def _init_node(state : AgentState) ->AgentState:
    state.setdefault("plan" ,[])
    state.setdefault("current_step",0)
    state.setdefault("max_steps",6)
    state.setdefault("rag_results", [])
    state.setdefault("final_answer", "")
    state.setdefault("memory",[])
    state.setdefault("errors",[])
    state.setdefault("iteration",0)
    state.setdefault("tool_calls", [])
    state["start_time"] = datetime.now().isoformat()
    
    return state

def _extract_plan_list(parsed):
    """
    Ollama's format="json" guarantees valid JSON, but NOT that the top-level
    shape is a bare array - instruct-tuned models often wrap a requested
    array in an object anyway, e.g. {"steps": [...]} or {"plan": [...]}.
    Accept the bare-array case (what we asked for) and the common
    dict-wrapped cases, so a well-formed answer never gets thrown away
    just because of the wrapper.
    """
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in ("steps", "plan", "actions", "tasks"):
            if isinstance(parsed.get(key), list):
                return parsed[key]
        # last resort 1: a dict with exactly one list-valued key
        list_values = [v for v in parsed.values() if isinstance(v, list)]
        if len(list_values) == 1:
            return list_values[0]
        # last resort 2: qwen3 sometimes turns "give me a list" into an
        # object whose keys AND values are both the step text itself
        # (e.g. {"Search the PDFs": "Search the PDFs", "Save it": "Save it"})
        # to satisfy an object-only JSON mode while still trying to comply.
        # If every value is a plain non-empty string, treat the values as
        # the ordered step list rather than throwing a good plan away.
        str_values = [v for v in parsed.values() if isinstance(v, str) and v.strip()]
        if parsed and len(str_values) == len(parsed):
            return str_values
    return None

_FILENAME_PATTERN = re.compile(
    r'(?:to|as|into|save\s+to|write\s+to|save\s+it\s+to|write\s+it\s+to)\s+'
    r'([\w\-\.]+\.(?:md|txt|json|csv|docx|xlsx))',
    re.IGNORECASE
)

def _extract_filename(text: str) -> str | None:
    """Extract filename from text like 'save it to report.md'."""
    match = _FILENAME_PATTERN.search(text)
    return match.group(1) if match else None
def plan_node(state: AgentState)->AgentState:
    """
    Ask the LLM to break the task into a short ordered list of concrete
    steps. One planning call up front is far cheaper than re-planning on
    every step, and is sufficient for this agent's two-tool workflow
    (retrieve from PDFs, optionally save the result to a file).
    """
    
    system = (
        "Break the user's task into 1-4 short, concrete steps for an agent "
        "with exactly two tools:\n"
        "  - rag_search: retrieves an answer from the user's uploaded PDFs\n"
        "  - write_output: saves text to a file\n\n"
        "Only include a write_output step if the user explicitly asked to "
        "save, export, or write the result to a file.\n"
        'Respond with ONLY a JSON object of the form {"steps": [...]}, '
        "where the value is a list of short step strings, nothing else. "
        'Example: {"steps": ["Search the PDFs for the refund policy", '
        '"Save the answer to refund_policy.md"]}'
    )
    
    raw_content = None
    try:
        resp = _llm.invoke([
            {"role" : "system",  "content" : system},
            {"role" : "user" , "content" : state["task"]}
        ])
        raw_content = resp.content
 
        parsed = json.loads(_clean_json(raw_content))
        plan = _extract_plan_list(parsed)
 
        if not plan:
            raise ValueError(f"planner returned an empty or malformed plan (raw: {raw_content!r})")
    except Exception as e:
        plan = ["search the pdfs to answer the task"]
        state['errors'].append(f"plan_node fallback used : {e}")
        
    state['plan'] = plan
    state['memory'].append({"node" : "plan" , "plan" : plan, "raw_llm_response": raw_content})
    if not state.get("file_path"):
        filename = _extract_filename(state["task"])
        if filename:
            state["file_path"] = f"outputs/{filename}"
    return state
 
_WRITE_KEYWORDS = ("save", "write", "export", "store", "persist")

def execute_step_node(state:AgentState)->AgentState:
    """
    Run exactly one plan step, then advance the cursor.

    Uses a cheap keyword router instead of an LLM call per step - the plan
    step text (produced by plan_node) already encodes the intended action,
    so a second LLM round-trip here would just add latency for no benefit.
    """
    
    idx = state["current_step"]
    step = state["plan"][idx]
    
    is_write_step = any(kw in step.lower() for kw in _WRITE_KEYWORDS)
    
    if is_write_step:
        content = state["final_answer"] or "\n\n".join(
            r.get("answer", "") for r in state["rag_results"] if r.get("answer")
        )
        
        path = state["file_path"]  or "outputs/agent_answer.md" 
        result = write_output(path=path, content=content)
        state["tool_calls"].append(f"write_output({path})")
        
        if not result.get("success"):
            state["errors"].append(result.get("error", "write_output failed"))
        else:
            state["file_path"] = result["path"]
    else:
        result = rag_search(query=state["task"])
        state["tool_calls"].append(f"rag_search({state['task'][:60]!r})")
        
        if result.get("success"):
            state["rag_results"].append(result)
            # Keep a running best-answer so a later write step (or
            # finalize, if the plan has no write step) always has
            # concrete content to work with.
            if result.get("answer"):
                state["final_answer"] = result["answer"]
        else:
            state["errors"].append(result.get("error", "rag_search failed"))
            
    state["memory"].append({"node": "execute_step", "step": step, "result": result})
    state["current_step"] += 1
    state["iteration"] +=1
    
    return state

def should_continue(state:AgentState)->str:
    """Router: keep executing plan steps, or move to finalize."""
    if state["current_step"] >= len(state["plan"]):
        return "finalize"
    
    if state["iteration"] >= state["max_steps"]:
        # Loop guard - guarantees termination even if the plan is
        # pathologically long or execute_step somehow never finishes it.
        return "finalize"
    return "execute_step"

def finalize_node(state:AgentState)->AgentState:
    """
    Compose the final answer from everything gathered. If retrieval never
    produced an answer, say so honestly instead of inventing one.
    """
    
    if not state["final_answer"]:
        if state["rag_results"]:
            state["final_answer"] = state["rag_results"][-1].get(
                "answer", "No answer could be generated from the retrieved context."
            )
        else:
            state["final_answer"] = (
                "I wasn't able to retrieve relevant information from the "
                "PDFs to answer this task."
            )
    state["memory"].append({"node": "finalize"})
    return state
    
        