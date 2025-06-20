import click
import time
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def start_otlp_metrics(endpoint: str = "http://localhost:4317") -> None:
    exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)


@click.group()
def metrics_cli() -> None:
    """Metrics and observability commands."""
    pass


@metrics_cli.command("serve")
@click.option("--endpoint", "-e", default="http://localhost:4317", help="OTLP endpoint (default: %(default)s)")
def serve(endpoint: str) -> None:
    """Serve metrics via OpenTelemetry OTLP."""
    click.echo(f"Starting metrics export to {endpoint} …")
    start_otlp_metrics(endpoint)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        click.echo("Metrics server stopped.")
