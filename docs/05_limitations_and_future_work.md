# Limitations and Future Work

## Limitations

### Enumeration completeness under high obligation density

Single-time enumeration accounts for 112/194 rejected answers = 57.73%, and every slot-bearing question in this subgroup requires at least three evidence obligations. The system resolves individual obligations strongly, but the language model does not always preserve every value when consolidating several obligations into one response.

### Answer-generation ceiling after slot-level evidence success

In 167/194 rejected answers = 86.08%, strict slot traces were complete, yet the final general-purpose language model produced an incomplete, incorrect, or overly abstaining response. Observed behaviours include omitted values, available evidence marked unavailable, incorrect comparison outcomes, and failure to preserve all supplied values.

### Single-domain evaluation

The current evaluation focuses on ECT-QA and earnings-call transcripts. ChronoRAG-G targets longitudinal evidence reasoning generally, but performance outside finance remains to be established empirically.

### Cross-system protocol differences

The contextual leaderboard aligns updated-corpus query partitions, but retrieval, prompting, and adjudication protocols differ across systems. It compares reported whole-pipeline outcomes rather than identical reimplementations.

### Deferred semantic resolution trade-off

Preserving conflicting and revised observations increases the burden on temporal compatibility checking and downstream answer construction. The architecture therefore depends on reliable metadata and explicit source-period/target-period handling.

## Future work

### 1. Explicit source-period and target-period representation

Future evidence records should distinguish when a statement was made, the period to which its value applies, and the period requested by the question. This direction also supports deferred semantic resolution by keeping source/statement period and target/value period metadata available until question-specific temporal resolution.

### 2. Time-parameterized retrieval representations

Period-conditioned representations or explicit temporal coordinates may help distinguish semantically similar evidence belonging to different temporal scopes.

### 3. Richer end-to-end trace instrumentation

Future traces should preserve the conceptual path:

```text
planned obligation
→ retrieved candidates
→ temporal decision
→ selected evidence
→ slot allocation
→ answer payload
→ structured answer
→ grounding
→ rendered output
```

### 4. Automated incremental GTCC updating

Production use requires incremental normalized-record, index, embedding, provenance, version, and consistency updates without rebuilding the full corpus.

### 5. Cross-domain validation

Additional longitudinal domains should be evaluated to distinguish architecture components that transfer unchanged from those requiring domain adaptation.
