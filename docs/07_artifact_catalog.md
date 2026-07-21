# Artifact Catalog

## Result tables

Every table is supplied in CSV, Markdown, and LaTeX.

| ID  | Table                             | Purpose                                                   |
| --- | --------------------------------- | --------------------------------------------------------- |
| 01  | Overall audited answer accuracy   | Headline 811/1,005 result and Wilson interval             |
| 02  | Accuracy by query subset          | Base and new partition results                            |
| 03  | Query subset × reasoning          | Reasoning behavior within base and new partitions         |
| 04  | Accuracy by reasoning type        | Enumeration, comparison, and unanswerable                 |
| 05  | Accuracy by temporal scope        | Single-time, multi-time, and relative-time                |
| 06  | Reasoning × temporal scope        | Detailed performance matrix                               |
| 07  | Reasoning × audit cohort          | Audited-right and ambiguous cohort composition            |
| 08  | Overall evidence resolution       | Strict, micro, and hybrid measures                        |
| 09  | Slot coverage by query subset     | Evidence resolution for base and new queries              |
| 10  | Slot coverage by reasoning type   | Obligation resolution across reasoning classes            |
| 11  | Slot coverage by temporal scope   | Obligation resolution across temporal classes             |
| 12  | Answer × trace contingency        | Accepted/rejected outcomes by trace condition             |
| 13  | Conditional failure decomposition | Trace-complete, incomplete, and slotless rejected answers |
| 14  | Contextual pipeline leaderboard   | Reported updated-corpus whole-pipeline outcomes           |
| 15  | TG-RAG answer-model sensitivity   | Published answer-model variation inside TG-RAG            |
| 16  | Pending-human accounting          | Frozen result and theoretical all-19-flip ceiling         |
| 17  | Public claim eligibility          | Approved, caveated, and forbidden formulations            |

## Result figures

Every figure is supplied in SVG, PNG, and PDF.

| ID  | Figure                            | Purpose                                     |
| --- | --------------------------------- | ------------------------------------------- |
| 01  | Answer accuracy by query subset   | Base/new accuracy                           |
| 02  | Answer accuracy by reasoning      | Enumeration/comparison/unanswerable         |
| 03  | Answer accuracy by temporal scope | Single/multi/relative time                  |
| 04  | Reasoning × temporal heatmap      | Detailed accuracy hotspot                   |
| 05  | Audit six-cell heatmap            | Cohort composition                          |
| 06  | Slot-coverage summary             | Strict, micro, and hybrid evidence measures |
| 07  | Failure-condition heatmap         | Trace conditions among rejected answers     |
| 08  | Contextual pipeline comparison    | Result-level leaderboard                    |

## Architecture diagrams

Every architecture diagram is supplied as one editable JSON source and one SVG/PNG/PDF rendering triplet.

| ID                                          | Source                                                                | SVG                                                                  | PNG                                                                  | PDF                                                                  |
| ------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 01_global_architecture                      | architecture/sources/01_global_architecture.json                      | architecture/figures/01_global_architecture.svg                      | architecture/figures/01_global_architecture.png                      | architecture/figures/01_global_architecture.pdf                      |
| 02_planning_and_obligations                 | architecture/sources/02_planning_and_obligations.json                 | architecture/figures/02_planning_and_obligations.svg                 | architecture/figures/02_planning_and_obligations.png                 | architecture/figures/02_planning_and_obligations.pdf                 |
| 03_per_slot_retrieval_and_temporal_control  | architecture/sources/03_per_slot_retrieval_and_temporal_control.json  | architecture/figures/03_per_slot_retrieval_and_temporal_control.svg  | architecture/figures/03_per_slot_retrieval_and_temporal_control.png  | architecture/figures/03_per_slot_retrieval_and_temporal_control.pdf  |
| 04_slot_preserving_allocation_and_answering | architecture/sources/04_slot_preserving_allocation_and_answering.json | architecture/figures/04_slot_preserving_allocation_and_answering.svg | architecture/figures/04_slot_preserving_allocation_and_answering.png | architecture/figures/04_slot_preserving_allocation_and_answering.pdf |
| 05_evaluation_and_trace_measurement         | architecture/sources/05_evaluation_and_trace_measurement.json         | architecture/figures/05_evaluation_and_trace_measurement.svg         | architecture/figures/05_evaluation_and_trace_measurement.png         | architecture/figures/05_evaluation_and_trace_measurement.pdf         |

## Code and examples

The repository includes public-safe contracts, schemas, validators, exact aggregate metric arithmetic, synthetic corpus records, and offline demonstrations. It does not include the private production runtime.
