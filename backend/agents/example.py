"""Example standalone demo demonstrating the minimal LangGraph marine workflow."""

import json
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.agents import run_minimal_marine_graph, MarineState


def main():
    query = "I'm near Mangalore. Where should I fish tomorrow morning?"
    print(f"Executing minimal LangGraph workflow for query:\n  '{query}'\n")

    # Run minimal workflow (understand_query -> planner -> END)
    state: MarineState = run_minimal_marine_graph(query, user_type="fisherman")

    print("=== RESULTING MARINE STATE ===")
    print(f"• Query:        {state.get('query')}")
    print(f"• User Type:    {state.get('user_type')}")
    print(f"• Intent:       {state.get('intent')} (Confidence: {state.get('confidence')})")
    print(f"• Location:     {json.dumps(state.get('location'), indent=2)}")
    print(f"• Time Range:   {json.dumps(state.get('time_range'), indent=2)}")
    print(f"• Variables:    {state.get('variables')}")

    exec_plan = state.get("execution_plan")
    if exec_plan:
        print("\n=== STRUCTURED EXECUTION PLAN ===")
        print(f"• Plan ID:     {exec_plan.plan_id}")
        print(f"• Summary:     {exec_plan.summary}")
        print(f"• Steps Count: {len(exec_plan.steps)}")
        print("• Steps Detail:")
        for step in exec_plan.steps:
            dep_str = f" [depends on: {', '.join(step.depends_on)}]" if step.depends_on else " [independent/parallel]"
            req_str = "mandatory" if step.required else "optional"
            print(f"  - [{step.type}] {step.id} ({step.operation}) | {req_str}{dep_str}")

    print(f"\n• Errors:       {state.get('errors')}")


if __name__ == "__main__":
    main()
