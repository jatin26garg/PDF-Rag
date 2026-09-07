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

def _intit_node(state : AgentState) ->AgentState:
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
        "Respond with ONLY a JSON array of short step strings, nothing else. "
        'Example: ["Search the PDFs for the refund policy", '
        '"Save the answer to refund_policy.md"]'
    )
    
    try:
        resp = _llm.invoke([
            {"role" : "system",  "content" : system},
            {"role" : "user" , "content" : state["task"]}
        ])
        
        plan = json.loads(_clean_json(resp.content))
        
        if not isinstance(plan,list) or not plan:
            raise ValueError("planner returned an empty or malformed plan")
    except Exception as e:
        plan = ["search the pdfs to answer the task"]
        state['errors'].append(f"plan_node fallback used : {e}")
        
    state['plan'] = plan
    state['memory'].append({"node" : "plan" , "plan" : plan})
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
        path = state.get("file_path") or "outputs/agent_answer.md"
        result = write_output(path=path, content=content)
        state["tool_calls"].append(f"write_output({path})")
        
        if not result.get("success"):
            state["errors"].append(result.get("error", "write_output failed"))
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
    
        