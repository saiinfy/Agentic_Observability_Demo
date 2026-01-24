"""
This module implements the Knowledge Agent, which enriches the incident state with contextual knowledge using a generative AI model (Gemini).

Functions:
    knowledge_agent(state):
        - Uses the incident signature (type, affected area, context) to construct a prompt.
        - Invokes the Gemini generative AI model to retrieve common causes and typical fixes for the incident.
        - Updates the state with the knowledge signal, including known cause, suggested fix, and a confidence hint.

Responsibilities:
- Provide contextual knowledge for incident analysis.
- Integrate with Gemini via the LangChain interface.
- Ensure observability with OpenTelemetry tracing.

Usage:
    Used as a node in the decision graph to supplement evidence with AI-driven knowledge for downstream decision-making.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from opentelemetry import trace

from state import state
tracer = trace.get_tracer("knowledge-agent")
from config.settings import  GEMINI_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GEMINI_KEY,
    temperature=0
)

def knowledge_agent(state):
 with tracer.start_as_current_span("context_lookup"):
    signature = state["incident_signature"]

    incident_type = signature.get("incident_type")
    affected_area = signature.get("affected_area")
    context = signature.get("context")

    prompt = f"""
You are providing contextual knowledge only.

Incident type: {incident_type}
Affected area: {affected_area}
Context: {context}

Return:
- common_cause
- typical_fix
"""

    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("llm.provider", "gemini")
        span.set_attribute("llm.model", "gemini-flash-latest")

        result = llm.invoke(prompt)

    # Handle Gemini response shape
        if isinstance(result.content, list):
            response_text = result.content[0].get("text", "")
        else:
            response_text = result.content

        state["knowledge_signal"] = {
            "known_cause": response_text,
            "suggested_fix": response_text,
            "confidence_hint": 0.5  # bounded, never dominant
            }

        return state