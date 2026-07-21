# Synthetic contract demonstration

All entities, properties, dates, values, and records in this directory are
invented. The example loads and validates each public contract, confirms that
one physical record can support two logical requirements, and computes a
strict slot-resolution result.

Run from the repository root:

```bash
python examples/synthetic/run_demo.py
```

The example demonstrates public contracts and metric calculation. It does not
implement or approximate the private ChronoRAG-G retrieval, ranking, prompting,
provider or grounding engine.
