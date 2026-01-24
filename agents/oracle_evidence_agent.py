"""
This module implements the Oracle Evidence Agent, responsible for retrieving evidence from an Oracle database using vector similarity search.

Functions:
    oracle_evidence_agent(state):
        - Generates an embedding for the user's issue description.
        - Connects to the Oracle database and performs a VECTOR similarity search against historical incident playbooks.
        - Aggregates evidence such as incident count, success rate, common resolution, and similarity score.
        - Handles errors gracefully, ensuring the decision graph does not crash.
        - Updates the state with evidence and status, but does not make decisions.

Responsibilities:
- Embedding generation for customer issues.
- Oracle VECTOR similarity search for relevant playbooks.
- Evidence aggregation for downstream decision-making.
- Safe error handling and status reporting.

Usage:
    Used as a node in the decision graph to enrich the state with Oracle-derived evidence for incident analysis.
"""

import oracledb
from opentelemetry import trace

from agents.embedding_utils import generate_embedding
from config.settings import MAX_VECTOR_DISTANCE,DB_HOST,DB_PASSWORD

tracer = trace.get_tracer("oracle-evidence-agent")


def oracle_evidence_agent(state):
    """
    Oracle Evidence Agent

    Responsibilities:
    - Generate embedding for customer issue
    - Perform Oracle VECTOR similarity search
    - Aggregate success/failure evidence
    - Fail safely on errors (never crash the graph)

    This agent NEVER decides.
    """

    with tracer.start_as_current_span("oracle_vector_similarity_search") as span:
        try:
            # ----------------------------
            # Validate required input
            # ----------------------------
            issue_text = state.get("user_description")
            if not issue_text:
                state["oracle_evidence"] = None
                state["evidence_status"] = "NOT_FOUND"
                return state

            # ----------------------------
            # Generate embedding (Python-side)
            # ----------------------------
            query_vector = generate_embedding(issue_text)

            # ----------------------------
            # Oracle connection
            # ----------------------------
            conn = oracledb.connect(
                user="system",
                password=DB_PASSWORD,
                host=DB_HOST,
                port=1521,
                service_name="FREEPDB1"
            )

            cursor = conn.cursor()

            # Explicit VECTOR binding (critical)
            cursor.setinputsizes(query_vec=oracledb.DB_TYPE_VECTOR)

            # ----------------------------
            # Vector similarity search
            # Deterministic ordering ensured
            # ----------------------------
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_matches,
                    AVG(success) AS success_ratio,
                    MAX(action_taken) KEEP (
                        DENSE_RANK FIRST
                        ORDER BY VECTOR_DISTANCE(embedding, :query_vec), id
                    ) AS best_action,
                    MIN(VECTOR_DISTANCE(embedding, :query_vec)) AS best_distance
                FROM incident_playbooks
                """,
                query_vec=query_vector,
            )

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            # ----------------------------
            # No evidence found
            # ----------------------------
            if not row or row[0] == 0:
                state["oracle_evidence"] = None
                state["evidence_status"] = "NOT_FOUND"
                return state

            best_distance = float(row[3])

            # Reject weak similarity matches
            if best_distance > MAX_VECTOR_DISTANCE:
                state["oracle_evidence"] = None
                state["evidence_status"] = "NOT_FOUND"
                return state

            similarity_score = max(0.0, 1.0 - best_distance)

            # ----------------------------
            # Populate evidence
            # ----------------------------
            state["oracle_evidence"] = {
                "incident_count": int(row[0]),
                "success_rate": float(row[1] or 0.0),
                "common_resolution": row[2],
                "similarity_score": round(similarity_score, 2),
            }

            state["evidence_status"] = "FOUND"

            # ----------------------------
            # Observability attributes
            # ----------------------------
            span.set_attribute("db.system", "oracle")
            span.set_attribute("db.operation", "vector_similarity_search")
            span.set_attribute("oracle.matches", row[0])
            span.set_attribute("oracle.similarity", similarity_score)
            span.set_attribute("oracle.success_rate", row[1])

            return state

        except Exception as e:
            # ----------------------------
            # HARD FAILURE → SAFE ESCALATION
            # ----------------------------
            state["oracle_evidence"] = None
            state["evidence_status"] = "ERROR"

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))

            return state
