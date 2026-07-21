# Architecture Diagrams

Five public-safe architecture diagrams are included as editable deterministic JSON sources plus SVG, PNG, and PDF renderings. The diagrams use synthetic labels and aggregate metrics only; private ranking equations, prompts, provider configuration, production constants, private traces, and infrastructure details are intentionally omitted.

Regenerate all architecture outputs from the repository root with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_architecture_diagrams.py
```

| Diagram | Editable source | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 01_global_architecture | sources/01_global_architecture.json | figures/01_global_architecture.svg | figures/01_global_architecture.png | figures/01_global_architecture.pdf |
| 02_planning_and_obligations | sources/02_planning_and_obligations.json | figures/02_planning_and_obligations.svg | figures/02_planning_and_obligations.png | figures/02_planning_and_obligations.pdf |
| 03_per_slot_retrieval_and_temporal_control | sources/03_per_slot_retrieval_and_temporal_control.json | figures/03_per_slot_retrieval_and_temporal_control.svg | figures/03_per_slot_retrieval_and_temporal_control.png | figures/03_per_slot_retrieval_and_temporal_control.pdf |
| 04_slot_preserving_allocation_and_answering | sources/04_slot_preserving_allocation_and_answering.json | figures/04_slot_preserving_allocation_and_answering.svg | figures/04_slot_preserving_allocation_and_answering.png | figures/04_slot_preserving_allocation_and_answering.pdf |
| 05_evaluation_and_trace_measurement | sources/05_evaluation_and_trace_measurement.json | figures/05_evaluation_and_trace_measurement.svg | figures/05_evaluation_and_trace_measurement.png | figures/05_evaluation_and_trace_measurement.pdf |

Publication captions and accessibility alt text are in [CAPTIONS.md](CAPTIONS.md).
