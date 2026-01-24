"""
Centralized configuration module for decision governance and policy settings in the incident decision agent system.

This file contains policy values only—modifying these does not require code changes elsewhere in the application.

Sections:
- Confidence & Decision Policy: Thresholds and weights for automated decision-making.
- Database / Evidence Policy: Parameters for evidence evaluation and similarity checks.
- Observability: Service name for tracing and monitoring.
- Incident Normalization: Standardized incident types and affected areas for classification.

Key Settings:
- CONFIDENCE_THRESHOLD: Minimum confidence for autonomous actions.
- SIMILARITY_WEIGHT, SUCCESS_WEIGHT: Weights for confidence calculation.
- NO_EVIDENCE_CONFIDENCE, ERROR_CONFIDENCE: Fallback values for confidence.
- MAX_VECTOR_DISTANCE: Maximum allowed vector distance for similarity.
- SERVICE_NAME: Identifier for observability/tracing.
- INCIDENT_TYPES, AFFECTED_AREAS: Lists for incident classification.
- GEMINI_KEY: API key for Gemini integration (keep secure).

Usage:
    Import and reference these constants throughout the application to enforce policy and configuration.
"""

# ---------------------------
# Confidence & Decision Policy
# ---------------------------

# Minimum confidence required for autonomous action
CONFIDENCE_THRESHOLD = 0.75

# Confidence computation weights
SIMILARITY_WEIGHT = 0.6
SUCCESS_WEIGHT = 0.4

# Fallback confidence values
NO_EVIDENCE_CONFIDENCE = 0.3
ERROR_CONFIDENCE = 0.0


# ---------------------------
# Database / Evidence Policy
# ---------------------------

# Max vector distance allowed to even consider similarity
MAX_VECTOR_DISTANCE = 0.6


# ---------------------------
# Observability
# ---------------------------

SERVICE_NAME = "incident-decision-agent"

# ---------------------------
# Incident Normalization
# ---------------------------

INCIDENT_TYPES = [
    "service_outage",
    "service_degradation",
    "configuration_error",
    "deployment_issue",
    "unknown_but_classified"
]

AFFECTED_AREAS = [
    "payments",
    "login",
    "orders",
    "delivery",
    "general"
]

GEMINI_KEY=""
DB_HOST=""
DB_PASSWORD=""
JAEGER_ENDPOINT=""
