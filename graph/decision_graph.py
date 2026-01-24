"""
This module defines the construction of the decision graph for the incident decision agent workflow using LangGraph.

Functions:
    build_decision_graph():
        Builds and compiles a stateful decision graph that orchestrates the flow of incident analysis and resolution.

Workflow Nodes:
- interpreter: Processes the initial user input and interprets the incident description.
- oracle_evidence: Gathers evidence from Oracle data sources.
- knowledge: Retrieves additional knowledge or context.
- orchestrator: Makes decisions based on gathered evidence and knowledge.
- human_approval: Handles cases where human intervention is required.

Graph Flow:
1. Entry point is the interpreter node.
2. Normal flow: interpreter → oracle_evidence → knowledge → orchestrator.
3. Conditional: orchestrator routes to human_approval if needed, otherwise ends.
4. The human_approval node always ends the flow.

Usage:
    Call build_decision_graph() to obtain a compiled decision graph for use in the main application workflow.
"""

from langgraph.graph import StateGraph, END

from state.state import IncidentState
from agents.incident_understanding_agent import incident_understanding_agent
from agents.oracle_evidence_agent import oracle_evidence_agent
from agents.knowledge_agent import knowledge_agent
from agents.orchestrator import orchestrator
from agents.human_approval import human_approval


def build_decision_graph():
    graph = StateGraph(IncidentState)

    # ---- Register nodes ----
    graph.add_node("interpreter", incident_understanding_agent)
    graph.add_node("oracle_evidence", oracle_evidence_agent)
    graph.add_node("knowledge", knowledge_agent)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("human_approval", human_approval)

    # ---- Entry point: customer language ----
    graph.set_entry_point("interpreter")

    # ---- Normal flow ----
    graph.add_edge("interpreter", "oracle_evidence")
    graph.add_edge("oracle_evidence", "knowledge")
    graph.add_edge("knowledge", "orchestrator")

    # ---- Conditional governance ----
    graph.add_conditional_edges(
        "orchestrator",
        lambda state: "human_approval" if state["requires_human"] else END,
        {
            "human_approval": "human_approval",
            END: END,
        },
    )

    # ---- Human always ends flow ----
    graph.add_edge("human_approval", END)

    return graph.compile()
