#!/usr/bin/env python
"""
Test script for the Agent Orchestrator.
Run this to see the agent in action.
"""

import json
from app.agent.orchestrator import run_agent


def test_agent():
    # Test 1: Simple search (no file save)
    print("\n" + "="*60)
    print("🧪 TEST 1: Search only")
    print("="*60)
    result = run_agent("What is the vacation policy?")
    print(f"\n✅ Final Answer:\n{result.get('final_answer')}")
    print(f"\n📋 Tool Calls: {result.get('tool_calls', [])}")
    print(f"📚 RAG Results: {len(result.get('rag_results', []))}")
    print(f"⚠️ Errors: {result.get('errors', [])}")

    # Test 2: Search and save
    print("\n" + "="*60)
    print("🧪 TEST 2: Search and save to file")
    print("="*60)
    result = run_agent(
        task="Summarize the vacation policy and save it to vacation_policy.md",
        file_path="outputs/vacation_policy.md",
        max_steps=5
    )
    print(f"\n✅ Final Answer:\n{result.get('final_answer')}")
    print(f"📁 File Path: {result.get('file_path')}")
    print(f"📋 Tool Calls: {result.get('tool_calls', [])}")
    print(f"📚 RAG Results: {len(result.get('rag_results', []))}")
    print(f"⚠️ Errors: {result.get('errors', [])}")

    # Test 3: Complex task (no file)
    print("\n" + "="*60)
    print("🧪 TEST 3: Complex query without file")
    print("="*60)
    result = run_agent(
        task="Find all policies related to employee leave and summarize them.",
        max_steps=4
    )
    print(f"\n✅ Final Answer:\n{result.get('final_answer')[:200]}...")
    print(f"📋 Tool Calls: {result.get('tool_calls', [])}")


if __name__ == "__main__":
    test_agent()