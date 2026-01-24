"""
This module configures OpenTelemetry tracing for the incident decision agent service.

Functions:
    setup_tracing():
        Sets up the OpenTelemetry tracer provider with a resource name, configures an OTLP exporter to send traces to a specified endpoint, and attaches a batch span processor to the provider.

Details:
- Uses OpenTelemetry SDK for Python.
- Exports traces to an OTLP-compatible backend via gRPC.
- The service is identified as 'incident-decision-agent'.
- The OTLP endpoint is set to 'http://54.174.185.20:4317' with insecure (non-TLS) communication.

Usage:
    Call setup_tracing() at the start of your application to enable distributed tracing.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from config.settings import JAEGER_ENDPOINT

def setup_tracing():
    resource = Resource.create({
        "service.name": "incident-decision-agent"
    })

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=JAEGER_ENDPOINT,
        insecure=True,
    )

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
