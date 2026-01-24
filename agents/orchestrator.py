"""
This module implements the orchestrator agent responsible for making confidence-based decisions in the incident resolution workflow.

Functions:
    orchestrator(state):
        Analyzes the current incident state, evaluates evidence, computes a confidence score, and determines whether the issue can be auto-resolved or requires human intervention. Sets the final decision and response message accordingly.

Decision Logic:
- If evidence retrieval failed (ERROR), escalate for manual review.
- If no historical evidence found (NOT_FOUND), require human review.
- If evidence is available, compute confidence as a weighted sum of similarity and success rate.
- If confidence meets or exceeds the threshold, auto-resolve; otherwise, require human review.
- Observability: Decision confidence and human requirement are traced as span attributes.

Usage:
    Called as a node in the decision graph to process and update the incident state.
"""

from opentelemetry import trace

from config.settings import (
    CONFIDENCE_THRESHOLD,
    SIMILARITY_WEIGHT,
    SUCCESS_WEIGHT,
    NO_EVIDENCE_CONFIDENCE,
    ERROR_CONFIDENCE
)


tracer = trace.get_tracer("orchestrator")


def orchestrator(state):
    with tracer.start_as_current_span("confidence_decision") as span:

        # 🔹 System failure → forced human
        if state["evidence_status"] == "ERROR":
            state["confidence"] = ERROR_CONFIDENCE
            state["requires_human"] = True
            state["final_decision"] = "SYSTEM_ESCALATION"
            state["response_message"] = (
                "Your issue has been escalated for manual review due to system constraints."
                    )
            return state

        # 🔹 No historical evidence → human, but not error
        if state["evidence_status"] == "NOT_FOUND":
            state["confidence"] = NO_EVIDENCE_CONFIDENCE
            state["requires_human"] = True
            state["final_decision"] = "REQUIRES_REVIEW"
            state["response_message"] = (
                "Your issue requires additional review by our engineering team."
                            )
            return state

        evidence = state["oracle_evidence"]

        similarity = evidence["similarity_score"]
        success_rate = evidence["success_rate"]

        confidence = round(
            (SIMILARITY_WEIGHT * similarity) + (SUCCESS_WEIGHT * success_rate),
            2
        )

        state["confidence"] = confidence
        state["requires_human"] = confidence < CONFIDENCE_THRESHOLD

        if not state["requires_human"]:
            state["final_decision"] = "AUTO_RESOLUTION"
            state["response_message"] = (
                f"We identified a known issue and applied a proven resolution: "
                f"{evidence['common_resolution']}."
            )

        # 🔹 Observability
        span.set_attribute("decision.confidence", confidence)
        span.set_attribute("decision.requires_human", state["requires_human"])

        return state
