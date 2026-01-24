"""
This module provides utilities for generating vector embeddings from text using a pre-trained sentence transformer model.

Functions:
    generate_embedding(text: str):
        - Encodes the input text into a vector embedding using the 'all-MiniLM-L6-v2' model.
        - Returns the embedding as a Python list of floats, suitable for use with Oracle VECTOR columns.

Responsibilities:
- Provide a simple interface for text-to-vector conversion.
- Use a lightweight, widely adopted model for efficient embedding generation.

Usage:
    Import and call generate_embedding(text) to obtain embeddings for natural language input in downstream agents or database operations.
"""

from sentence_transformers import SentenceTransformer
from opentelemetry import trace

tracer = trace.get_tracer("embedding-tool")

# Lightweight, widely used, 384-dim
_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str):
    """
    Returns a Python list of floats suitable for Oracle VECTOR.
    """
    with tracer.start_as_current_span("embedding_generation") as span:
        span.set_attribute("embedding.model", "all-MiniLM-L6-v2")
        span.set_attribute("embedding.input_length", len(text))

        vector = _model.encode(text)
        return vector.tolist()
