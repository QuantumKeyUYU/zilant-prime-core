Observability
=============

Run the metrics server and fetch Prometheus data::

   zilant metrics serve --port 9200 &
   curl http://localhost:9200/metrics | grep zilant_command_duration_seconds

Set ``ZILANT_TRACE=1`` to enable console tracing via OpenTelemetry.
