# Architecture

## Global flow

![ChronoRAG-G global architecture](architecture/figures/01_global_architecture.png)

ChronoRAG-G represents each requested fact as an ordered evidence obligation and preserves that logical identity through retrieval, temporal control, allocation, answer construction, and evaluation.

```text
question
→ ordered evidence obligations
→ per-slot retrieval
→ compatibility and temporal control
→ slot-preserving allocation
→ logical-to-physical registry
→ structured answer
→ grounding and bounded correction
→ finalization
→ answer and trace evaluation
```

## Ingestion boundary and deferred resolution

ChronoRAG-G distinguishes low-level ingestion from semantic resolution. Document parsing, text extraction, metadata validation, timestamp extraction, schema normalization, provenance capture, record construction, malformed-record rejection, technical duplicate handling where necessary, and indexing are performed during corpus construction. GTCC then preserves potentially conflicting values, revision history, historical state, and temporally incompatible evidence as structured evidence rather than collapsing conflicting values, overwriting historical states, discarding revised or superseded observations, forcing one canonical fact during ingestion, prematurely resolving temporal ambiguity, or removing evidence only because it conflicts with a later observation.

```text
source documents
→ parsing and metadata extraction
→ structural normalization and provenance capture
→ preservation of temporally distinct observations
→ slot-conditioned retrieval
→ question-specific temporal resolution
```

This deferred semantic resolution boundary lets source/statement period and target/value period metadata remain available to later compatibility checks. Question-specific resolution occurs during slot-conditioned retrieval, temporal compatibility checking, evidence allocation, and answer construction.

## 1. Planning and obligation construction

The planning stage converts the question into ordered atomic requirements. Each requirement contains the public information needed to identify one answer cell: entity, metric, requested period, temporal role, target type, and output position.

Malformed, duplicate, or incomplete obligations are rejected before retrieval.

![Planning and obligations](architecture/figures/02_planning_and_obligations.png)

Planning turns a synthetic question into stable ordered obligations with unique identity, typed target periods, and complete output coverage.

## 2. Per-slot retrieval

Every slot owns a candidate pool. The public abstraction allows deterministic candidate ordering and bounded pool growth without releasing production ranking constants or provider-specific behavior.

Candidates are deduplicated inside a slot. A physical record may remain relevant to several slots.

## GTCC and Controlled Candidate Expansion

GTCC is the runtime evidence substrate for the evaluated path. Each required slot searches the normalized embedding index built from 67,591 GTCC records. When a slot remains weak, controlled candidate expansion increases that slot's GTCC candidate view from 10 to 15, 20, and 25 records. The system merges and deduplicates returned GTCC records by stable identity, then uses GTCC temporal, semantic, provenance, and field-presence metadata during compatibility control, allocation, grounding, and trace reconstruction.

The frozen scoring path does not traverse adjacency edges. Graph structure preserves linked temporal records, relation metadata, document membership, provenance, and stable identity, while exact dense retrieval supplies candidate motion over the GTCC index. Controlled candidate expansion therefore depends on GTCC even though it is not classical graph traversal.

## 3. Compatibility and temporal control

Candidate compatibility is considered separately from semantic similarity. Described checks include:

- entity compatibility;
- metric compatibility;
- target-period compatibility;
- statement-period versus target-period distinction;
- metadata completeness;
- value-type and unit compatibility.

![Per-slot retrieval and temporal control](architecture/figures/03_per_slot_retrieval_and_temporal_control.png)

Per-slot retrieval keeps candidate pools and temporal checks local to each obligation while permitting physical evidence to remain relevant across slots.

## 4. Slot-preserving allocation

Allocation chooses logical slot-candidate pairs while tracking which physical records are included. If one physical record supports two obligations, both logical relationships remain visible while the physical record is counted once against the context budget.

## 5. Logical-to-physical registry

The registry links:

```text
logical obligation
→ selected support relation
→ physical evidence record
```

This avoids both double charging and logical collapse.

## 6. Answer construction

The answer payload preserves the obligation order and selected support. Enumeration questions require one explicit output component per obligation. Comparison questions require complete and compatible operands before the comparison result is rendered.

## 7. Grounding and bounded correction

Grounding validates answer components against allowed evidence references and compatible metadata. When a component is disputed, bounded correction reopens only the affected obligations.

![Slot-preserving allocation and answering](architecture/figures/04_slot_preserving_allocation_and_answering.png)

Allocation records logical-to-physical support relations so shared evidence does not collapse distinct answer requirements.

## 8. Finalization

Finalization derives the rendered answer from validated components. It does not invent values, silently convert incompatible units, or infer a comparison winner from incomplete evidence.

## 9. Evaluation flow

Answer acceptance, strict trace completeness, micro slot coverage, and hybrid evidence resolution remain separate. This separation exposes the difference between finding evidence and successfully rendering the final answer.

![Evaluation and trace measurement](architecture/figures/05_evaluation_and_trace_measurement.png)

Evaluation reports answer accuracy separately from strict trace coverage, micro required-slot coverage, and hybrid evidence resolution.
