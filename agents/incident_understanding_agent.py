"""
This module implements the Incident Understanding Agent, which classifies and interprets user-provided incident descriptions using a generative AI model (Gemini).

Functions:
    incident_understanding_agent(state):
        - Receives a user description of an incident.
        - Prompts the Gemini model to classify the incident into a known type and affected area, using only allowed values.
        - Parses the model's JSON response and updates the state with the incident signature (type, area, context).
        - Handles parsing errors with a controlled fallback.

Responsibilities:
- Interpret and classify customer issues for downstream processing.
- Enforce use of standardized incident types and affected areas.
- Integrate with Gemini via the LangChain interface.
- Ensure observability with OpenTelemetry tracing.

Usage:
    Used as the entry point node in the decision graph to transform user input into a structured incident signature.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from opentelemetry import trace
from config.settings import INCIDENT_TYPES, AFFECTED_AREAS, GEMINI_KEY

tracer = trace.get_tracer("incident-understanding-agent")

# Gemini is used ONLY for interpretation, not decisions
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GEMINI_KEY,
    temperature=0
)


def incident_understanding_agent(state):
    with tracer.start_as_current_span("incident_understanding") as span:
        description = state.get("user_description", "").strip()

        prompt = f"""
You are an incident classification system.

Your task:
- Classify the customer issue into a known incident type and affected area.
- Use ONLY the allowed values.
- If uncertain, choose the closest reasonable category.

Allowed incident_type values:
{INCIDENT_TYPES}

Allowed affected_area values:
{AFFECTED_AREAS}

Return ONLY valid JSON in this format:

{{
  "incident_type": "<one of allowed incident_type>",
  "affected_area": "<one of allowed affected_area>",
  "context": "<short free text context>"
}}

Customer issue:
\"\"\"{description}\"\"\"
"""

    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("llm.provider", "gemini")
        span.set_attribute("llm.model", "gemini-flash-latest")

        result = llm.invoke(prompt)
        # Gemini may return list or string
        if isinstance(result.content, list):
            response_text = result.content[0].get("text", "")
        else:
            response_text = result.content

        response_text = response_text.strip()

        try:
            parsed = json.loads(response_text)
        except Exception:
            # Controlled fallback — NOT "unknown"
            parsed = {
                "incident_type": "unknown_but_classified",
                "affected_area": "general",
                "context": "unspecified"
            }

        # -------------------------
        # Normalization (CRITICAL)
        # -------------------------

        if parsed.get("incident_type") not in INCIDENT_TYPES:
            parsed["incident_type"] = "unknown_but_classified"

        if parsed.get("affected_area") not in AFFECTED_AREAS:
            parsed["affected_area"] = "general"

        if not parsed.get("context"):
            parsed["context"] = "unspecified"

        state["incident_signature"] = parsed

        # -------------------------
        # Observability
        # -------------------------
        span.set_attribute("incident.type", parsed["incident_type"])
        span.set_attribute("incident.area", parsed["affected_area"])
        span.set_attribute(
            "incident.ambiguous",
            parsed["incident_type"] == "unknown_but_classified"
        )

        return state
