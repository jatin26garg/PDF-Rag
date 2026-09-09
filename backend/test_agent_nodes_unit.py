"""
Level 1 test: pure state-logic nodes, no LLM, no Qdrant, no file I/O.
Run from backend/: python -m pytest test_agent_nodes_unit.py -v
Or directly: python test_agent_nodes_unit.py
"""

from app.agent.nodes import _init_node, should_continue


def test_init_node_returns_state_and_sets_defaults():
    state = {"task": "test task"}
    result = _init_node(state)

    # This is the exact bug we just fixed - would fail loudly if it regresses
    assert result is not None, "_intit_node returned None - missing `return state`!"
    assert result["plan"] == []
    assert result["current_step"] == 0
    assert result["max_steps"] == 6
    assert result["rag_results"] == []
    assert result["errors"] == []
    assert result["tool_calls"] == []
    assert "start_time" in result
    print("PASS: init_node returns state with correct defaults")


def test_should_continue_finalizes_when_plan_done():
    state = {"current_step": 2, "plan": ["a", "b"], "iteration": 2, "max_steps": 6}
    assert should_continue(state) == "finalize"
    print("PASS: should_continue -> finalize when plan exhausted")


def test_should_continue_continues_mid_plan():
    state = {"current_step": 0, "plan": ["a", "b"], "iteration": 0, "max_steps": 6}
    assert should_continue(state) == "execute_step"
    print("PASS: should_continue -> execute_step mid-plan")


def test_should_continue_loop_guard():
    state = {"current_step": 0, "plan": ["a", "b", "c", "d", "e", "f", "g"],
              "iteration": 6, "max_steps": 6}
    assert should_continue(state) == "finalize"
    print("PASS: should_continue -> finalize when max_steps hit, even mid-plan")


if __name__ == "__main__":
    test_init_node_returns_state_and_sets_defaults()
    test_should_continue_finalizes_when_plan_done()
    test_should_continue_continues_mid_plan()
    test_should_continue_loop_guard()
    print("\nAll Level 1 tests passed.")