"""
This module defines the data structures for representing the state and evidence used in the incident decision workflow.

Classes:
    OracleEvidence (TypedDict):
        Represents evidence retrieved from Oracle, including incident count, success rate, common resolution, and similarity score.
    IncidentState (TypedDict):
        Represents the full state of an incident analysis, including user input, evidence, decision status, and customer-facing response.

Fields:
- user_description: The user's description of the issue.
- incident_signature: Signature or metadata for the incident.
- oracle_evidence: Evidence details from Oracle (see OracleEvidence).
- evidence_status: Status of evidence retrieval ("FOUND", "NOT_FOUND", or "ERROR").
- confidence: Confidence score for the automated decision.
- requires_human: Whether human approval is needed.
- final_decision: The final decision or action taken.
- response_message: Message to be shown to the customer.

Usage:
    Import these types to annotate and manage state in the incident decision agent workflow.
"""

from typing import TypedDict, Optional, Dict, Literal


class OracleEvidence(TypedDict):
    incident_count: int
    success_rate: float
    common_resolution: Optional[str]
    similarity_score: float


class IncidentState(TypedDict):
    user_description: Optional[str]
    incident_signature: Optional[Dict[str, str]]

    # Evidence
    oracle_evidence: Optional[OracleEvidence]

    # 🔹 NEW: evidence health
    evidence_status: Literal["FOUND", "NOT_FOUND", "ERROR"]

    # Decision
    confidence: Optional[float]
    requires_human: Optional[bool]
    final_decision: Optional[str]
    response_message: Optional[str]      # customer-facing
