# Architecture Captions

## 01_global_architecture - ChronoRAG-G: Obligation-Preserving Temporal QA Architecture

**Caption.** ChronoRAG-G represents each requested fact as an ordered evidence obligation and preserves that logical identity through retrieval, temporal control, allocation, answer construction, and evaluation. The diagram separates logical slots from physical evidence so that a record can support multiple obligations without collapsing the required answer components. The public abstraction intentionally omits private ranking equations, prompts, provider configuration, and production constants.

**Alt text.** A left-to-right and top-to-bottom pipeline shows a question becoming ordered evidence obligations, then moving through per-slot retrieval, temporal control, allocation, registry, answer construction, grounding, finalization, and evaluation. Group labels separate planning, evidence resolution, answer construction, and evaluation.

## 02_planning_and_obligations - From Question to Ordered Evidence Obligations

**Caption.** The planning stage converts one synthetic question into a stable ordered list of atomic evidence obligations. Each obligation records the entity, metric, and target period needed for one answer component, which lets downstream retrieval and evaluation preserve complete output coverage. The example uses synthetic entities only.

**Alt text.** A synthetic question passes through extraction and validation stages to produce four obligations for Acme Holdings and Beta Systems revenue and operating margin in FY2025 Q1.

## 03_per_slot_retrieval_and_temporal_control - Per-Slot Retrieval, Temporal Compatibility, and Evidence Control

**Caption.** Each logical slot owns its own retrieval path: a slot-specific query produces a candidate pool, then compatibility and temporal checks filter usable evidence. Candidate identity is deduplicated within a slot, but a physical record may still support multiple logical slots. Exact production ranking and weighting logic are not released.

**Alt text.** Three parallel paths labeled E1, E2, and E3 each move from slot-specific query to candidate pool, compatibility checks, temporal checks, and a usable candidate set. A side panel explains compatible and incompatible candidate states and the statement-period versus target-period distinction.

## 04_slot_preserving_allocation_and_answering - Slot-Preserving Allocation, Evidence Registry, and Answer Construction

**Caption.** Slot-preserving allocation records selected support relations between logical obligations and physical records while keeping the logical obligations distinct. In the synthetic mapping, record 2 supports two logical obligations and consumes physical context once, but E2 and E3 remain separate answer requirements. Grounding and bounded correction operate on individual components rather than an uncontrolled full-answer rewrite.

**Alt text.** Four logical obligations map to three physical records, with record 2 supporting both E2 and E3. A registry feeds structured answer components, grounding, bounded correction, and a final answer.

## 05_evaluation_and_trace_measurement - Answer Evaluation and Evidence-Resolution Measurement

**Caption.** Evaluation separates final answer acceptance from evidence-resolution measures. The 1,005-question cohort contains 882 slot-bearing and 123 slotless questions; strict and micro slot metrics apply to the slot-bearing branch, while answer accuracy and hybrid evidence resolution are measured over all questions. Hybrid evidence resolution is not answer accuracy and is not a conventional top-k retrieval metric.

**Alt text.** A cohort of 1,005 evaluated questions splits into 882 slot-bearing and 123 slotless questions. The diagram lists audited answer accuracy, strict trace-derived slot coverage, micro required-slot coverage, hybrid evidence resolution, and rejected-answer contingency counts.
