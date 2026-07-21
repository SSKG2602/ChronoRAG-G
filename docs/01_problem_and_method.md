# Research Problem and Method

## Research question

ChronoRAG-G studies whether temporal questions over longitudinal document collections can be answered more reliably by decomposing the question into ordered evidence obligations and preserving those obligations through retrieval, evidence allocation, answer construction, grounding, and evaluation.

## Why a single retrieval request is insufficient

Many financial questions contain a Cartesian structure: multiple entities, metrics, and periods must be resolved before the final operation can be performed. A shared top-k context can be semantically relevant while still omitting one requested answer cell. It can also mix actual results, forward guidance, and later references to the same metric.

ChronoRAG-G makes every required answer cell explicit.

## Deferred semantic resolution

Many retrieval pipelines are optimized for relatively stable knowledge and reduce inconsistency before retrieval. That strategy is useful when conflicting records are redundant or erroneous, but it can erase temporal information in longitudinal corpora. ChronoRAG-G instead treats inconsistency as potentially informative until the relevant temporal and semantic context is known.

ChronoRAG-G distinguishes low-level ingestion from semantic resolution. Document parsing, text extraction, metadata validation, timestamp extraction, schema normalization, provenance capture, and indexing are performed during corpus construction. However, GTCC does not force potentially conflicting observations into one canonical fact at ingestion time. Revisions, historical states, temporally distinct values, and unresolved evidence are retained in a structured representation so that their compatibility can be evaluated against the specific entity, metric, and target period requested by a question.

This design follows a deferred semantic resolution principle. Evidence is normalized structurally without prematurely collapsing its temporal meaning. A value that conflicts with another record may represent a different reporting period, a revised estimate, forward guidance, or a later historical state rather than simple noise. ChronoRAG-G therefore resolves such conflicts during slot-conditioned retrieval, temporal compatibility checking, evidence allocation, and answer construction, where the question supplies the context needed to determine relevance.

Deferred semantic resolution does not mean the absence of preprocessing. The corpus still undergoes parsing, validation, structural normalization, provenance capture, record construction, field validation, malformed-record rejection, technical duplicate handling where necessary, and indexing. The deferred operations are semantic: selecting which observation governs a particular question, determining whether two values are genuinely contradictory, and deciding whether an older or revised statement remains relevant.

This is not embedding unreviewed documents. It is temporal evidence preservation after low-level ingestion: semantically distinct observations, revision history, temporally incompatible evidence, source/statement period metadata, and target/value period metadata are preserved as structured evidence until a question supplies the context for resolution.

## Evidence obligations and slots

An evidence obligation is one atomic fact requirement. A slot is its runtime and evaluation representation. A typical slot corresponds to an entity, metric, and target period, with additional role or relation information where necessary.

The ordered plan is written conceptually as:

```text
P(q) = [E1, E2, ..., En]
```

Each obligation is independently resolvable, missing, or disputed. This makes partial evidence visible rather than allowing one successful retrieval to hide another missing requirement.

## Method

1. Parse the question into ordered obligations.
2. Validate that every obligation has a stable identifier and typed temporal request.
3. Retrieve candidates separately for each obligation.
4. apply entity, metric, and temporal compatibility controls.
5. Preserve slot ownership during evidence selection.
6. Deduplicate physical evidence without collapsing logical obligations.
7. Construct a structured answer from the selected evidence.
8. Ground each answer component against allowed evidence.
9. Finalize the response and compute answer-level and evidence-level metrics separately.

## Why order matters

The order of E1 through En stabilizes:

- retrieval ownership;
- evidence-table order;
- allocation order;
- answer-component order;
- grounding references;
- trace comparison.

Ordering does not assign importance. It makes the pipeline deterministic and auditable.

## Slotless questions

Some questions have no defined atomic evidence-slot denominator under the frozen evaluation contract. Strict trace coverage is undefined for these questions rather than being forced to zero or one. They remain part of answer accuracy and hybrid evidence resolution.
