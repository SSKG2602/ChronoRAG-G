# Evaluation and Results

## Benchmark

The frozen evaluation contains 1,005 ECT-QA questions over an updated corpus of 480 earnings-call transcripts.

## Headline result

ChronoRAG-G achieved 811/1,005 = 80.70% audited answer accuracy. The approximate 95% Wilson confidence interval is [78.14%, 83.02%].

## Query partitions

| Partition | Accepted | Rejected | Total | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Base / updated corpus | 517 | 139 | 656 | 78.81% |
| New / updated corpus | 294 | 55 | 349 | 84.24% |
| Overall | 811 | 194 | 1,005 | 80.70% |

New-query unanswerable accuracy was 101/101 = 100.00%.

## Reasoning type

| Type | Accepted | Rejected | Total | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Enumeration | 318 | 144 | 462 | 68.83% |
| Comparison | 240 | 42 | 282 | 85.11% |
| Unanswerable | 253 | 8 | 261 | 96.93% |

## Temporal scope

| Scope | Accepted | Rejected | Total | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Single-time | 359 | 124 | 483 | 74.33% |
| Multi-time | 283 | 38 | 321 | 88.16% |
| Relative-time | 169 | 32 | 201 | 84.08% |

## Evidence-level measures

### Strict trace-derived slot coverage

A slot-bearing question is strictly trace complete only when every required slot is complete under the frozen trace criterion.

```text
846 / 882 = 95.92%
```

### Micro required-slot coverage

```text
3,837 resolved required slots / 3,889 required slots = 98.66%
```

### Hybrid evidence resolution

```text
978 / 1,005 = 97.31%
```

Hybrid evidence resolution is a per-question evidence-resolution measure. It is distinct from audited answer accuracy and conventional top-k retrieval metrics.

## Answer and trace contingency

| Trace condition | Accepted | Rejected |
| --- | ---: | ---: |
| Strict trace complete | 679 | 167 |
| Trace incomplete | 14 | 22 |
| Slotless | 118 | 5 |

Among rejected answers, 167/194 = 86.08% had complete strict slot traces.

## Contextual leaderboard

The release includes a contextual result-level leaderboard under aligned updated-corpus query partitions. External combined results are denominator-weighted from published rounded Correct ratios.

ChronoRAG-G achieved 80.70%, compared with TG-RAG's combined 59.74%, a gap of approximately 20.95 percentage points. The systems use different retrieval, prompting, and adjudication protocols; the comparison is therefore result-level rather than an identical reimplementation.

## Frozen-score boundary

The public headline result is 811/1,005 = 80.70%. A theoretical 830/1,005 = 82.59% all-19-flip ceiling is reported only as human-review accounting and is not the frozen score.
