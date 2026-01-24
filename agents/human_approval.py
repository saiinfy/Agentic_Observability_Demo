"""
This module implements the Human Approval Agent, which handles cases requiring manual review and approval in the incident decision workflow.

Functions:
    human_approval(state):
        - Notifies the user that human review is required.
        - Displays the issue description, confidence score, and any suggested action based on historical evidence.
        - Prompts the human reviewer to approve or reject the proposed action.
        - Updates the state with the final decision and a customer-facing response message.

Responsibilities:
- Ensure human-in-the-loop governance for low-confidence or exceptional cases.
- Provide safe and clear evidence display for reviewers.
- Integrate with OpenTelemetry for observability.

Usage:
    Used as a node in the decision graph when automated resolution is not possible or requires human oversight.
"""

from opentelemetry import trace
tracer = trace.get_tracer("human-approval")


def human_approval(state):
    with tracer.start_as_current_span("human_gate"):

        print("\n⚠️  HUMAN REVIEW REQUIRED ⚠️")
        print("--------------------------------")

        print(f"Issue Description : {state['user_description']}")
        print(f"Confidence Score  : {state['confidence']}")

        # ---- Safe evidence display ----
        evidence = state.get("oracle_evidence")

        if evidence and evidence.get("common_resolution"):
            print("\nSuggested Action:")
            print(f"  - {evidence['common_resolution']}")
        else:
            print("\nSuggested Action:")
            print("  - No reliable historical action available")

        print("--------------------------------")

        decision = input("Proceed with action? (yes/no): ").strip().lower()

        if decision == "yes":
            state["final_decision"] = "HUMAN_APPROVED"
            state["response_message"] = (
                "Your issue has been reviewed and an appropriate action has been taken."
            )
        else:
            state["final_decision"] = "HUMAN_REJECTED"
            state["response_message"] = (
                "Your issue has been reviewed and escalated for further investigation."
            )

        return state
