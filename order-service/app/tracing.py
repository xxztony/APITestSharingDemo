import os
from collections.abc import Callable
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_CONFIGURED = False
_INSTRUMENTED: set[str] = set()


def _enabled() -> bool:
    return os.getenv("OTEL_SDK_DISABLED", "false").lower() not in {"true", "1", "yes"}


def _endpoint() -> str:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or "localhost:4317"
    endpoint = endpoint.removeprefix("http://").removeprefix("https://")
    endpoint = endpoint.removesuffix("/v1/traces")
    return endpoint


def _resource_attributes(default_service_name: str) -> dict[str, str]:
    attributes = {SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", default_service_name)}
    for item in os.getenv("OTEL_RESOURCE_ATTRIBUTES", "").split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            attributes[key.strip()] = value.strip()
    return attributes


def configure_tracing(default_service_name: str) -> None:
    global _CONFIGURED
    if _CONFIGURED or not _enabled():
        return
    provider = TracerProvider(resource=Resource.create(_resource_attributes(default_service_name)))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=_endpoint(), insecure=True)))
    trace.set_tracer_provider(provider)
    _CONFIGURED = True


def _safe_instrument(key: str, instrument: Callable[[], Any]) -> None:
    if key in _INSTRUMENTED or not _enabled():
        return
    try:
        instrument()
    except Exception as exc:
        print(f"OpenTelemetry instrumentation skipped for {key}: {exc}", flush=True)
        return
    _INSTRUMENTED.add(key)


def instrument_fastapi_app(app: Any) -> None:
    def _instrument() -> None:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)

    _safe_instrument(f"fastapi:{id(app)}", _instrument)


def instrument_sqlalchemy_engine(engine: Any) -> None:
    def _instrument() -> None:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument(engine=engine)

    _safe_instrument(f"sqlalchemy:{id(engine)}", _instrument)
