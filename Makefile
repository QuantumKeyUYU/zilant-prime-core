pq-wheels:
	python tools/build_pq_wheels.py


.PHONY: docs
docs:
	$(MAKE) -C docs mermaid html
