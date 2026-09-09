from typing import Optional

from langgraph.graph import StateGraph,END
from app.agent.state import AgentState
from app.agent.nodes import (_init_node,plan_node,execute_step_node,should_continue,finalize_node)


def build_agent():
    graph = StateGraph(AgentState)
    
    graph.add_node("init",_init_node)
    graph.add_node("plan", plan_node)
    graph.add_node("execute_step",execute_step_node)
    graph.add_node("finalize", finalize_node)
    
    graph.set_entry_point("init")
    graph.add_edge("init", "plan")
    graph.add_edge("plan","execute_step")
    
    graph.add_conditional_edges("execute_step", should_continue, {
        "execute_step" : "execute_step",
        "finalize" : "finalize"
    })
    
    graph.add_edge("finalize", END)
    
    return graph.compile()

_agent = build_agent()

def run_agent(task :str, file_path : Optional[str] = None, max_steps:int = 6, )->AgentState:
    """
    Run the agent end-to-end on a single task.

    Args:
        task: natural-language request, e.g. "Summarize the refund policy
              and save it to refund_summary.md"
        file_path: optional explicit output path (relative to workspace).
                   If omitted and a write step runs, defaults to
                   outputs/agent_answer.md
        max_steps: hard cap on execute_step iterations (loop safety net,
                   independent of how many steps the planner proposed)

    Returns:
        The final AgentState - `final_answer`, `rag_results`, `tool_calls`,
        and `errors` are the fields most useful for callers/observability.
    """
    
    initial_state: AgentState = {
        "task": task,
        "file_path": file_path,
        "max_steps": max_steps,
    }
    return _agent.invoke(initial_state)