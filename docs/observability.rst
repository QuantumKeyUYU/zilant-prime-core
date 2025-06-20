.. _observability:

Observability
=============

.. toctree::
   :maxdepth: 1

Metrics serve
-------------

Use the CLI command:

.. code-block:: bash

   zilant metrics serve --endpoint http://<OTLP_HOST>:4317

This will export internal metrics (Prometheus histograms, counts) via OpenTelemetry OTLP periodically.
