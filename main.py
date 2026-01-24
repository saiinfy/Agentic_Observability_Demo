"""
Main entry point for the Incident Decision Review Assistant application.

This script initializes telemetry tracing, collects a user-provided incident description, builds the decision graph, and executes the agentic flow to analyze the incident. The final outcome, including confidence score, human approval requirement, and a response message, is printed for the user.

Workflow:
1. Sets up OpenTelemetry tracing for distributed monitoring.
2. Prompts the user for a natural language description of their issue.
3. Builds the decision graph using the LangGraph framework.
4. Initializes the shared state for the agentic flow.
5. Executes the decision process within a tracing span.
6. Outputs the final results to the user.

Usage:
    python main.py

Requirements:
    - All dependencies listed in requirements.txt must be installed.
    - The supporting modules (graph, telemetry, etc.) must be present in the workspace.
"""

from graph.decision_graph import build_decision_graph
from telemetry import setup_tracing
from opentelemetry import trace


def main():
    setup_tracing()
    tracer = trace.get_tracer("incident-decision-app")

    print("\n=== Incident Decision Review Assistant ===\n")

    # 🔹 Customer-facing natural language input
    user_description = input("Describe your issue: ").strip()

    # 🔹 Build LangGraph
    graph = build_decision_graph()

    # 🔹 Initial shared state
    initial_state = {
        "user_description": user_description,
        "incident_signature": None,
        "oracle_evidence": None,
        "knowledge_signal": None,
        "confidence": None,
        "requires_human": None,
        "final_decision": None,
    }

    # 🔹 Execute agentic flow
    with tracer.start_as_current_span("incident_decision_flow"):
        final_state = graph.invoke(initial_state)

    # 🔹 Final outcome (customer-safe)
    print("\n--- FINAL OUTPUT ---")
    print(f"Issue Description     : {user_description}")
    print(f"Confidence Score      : {final_state['confidence']}")
    print(f"Human Approval Needed : {final_state['requires_human']}")
    print(f"Response              : {final_state['response_message']}")

    print("---------------------\n")


if __name__ == "__main__":
    main()
