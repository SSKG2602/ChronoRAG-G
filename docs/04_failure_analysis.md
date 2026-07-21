# Failure-Mode Analysis

## Analysis boundary

The public analysis separates complete-population descriptive findings from sampled diagnostic findings.

Complete-population counts describe where failures concentrate. The diagnostic sample examines concrete persisted evidence transitions. Sample categories are not extrapolated as prevalence estimates.

## Full-population descriptive findings

| Condition | Count | Share of rejected answers |
| --- | ---: | ---: |
| Rejected answers | 194 | 100.00% |
| Single-time enumeration | 112 | 57.73% |
| Strict trace complete | 167 | 86.08% |
| Trace incomplete | 22 | 11.34% |
| Slotless | 5 | 2.58% |

Single-time enumeration is the largest concentration. It reaches 162/274 = 59.12% accuracy, and every slot-bearing question in that subgroup contains at least three evidence obligations.

## Deterministic diagnostic sample

A bounded forensic review covered 43 rejected cases and 11 matched successful controls selected by deterministic diversity sampling.

Observed behaviours:

- five directly evidenced planning collapses;
- seven candidate-absence observations;
- nine temporal/source-target observations;
- twenty-two cases in which evidence was present but the final answer was rejected.

## Interpretation

The sample did not establish one universal causal stage. It did show that failure can arise at several points:

- a valid obligation plan is not produced;
- one requested value never reaches the usable candidate path;
- source period and target period are confused;
- selected evidence is not preserved into the answer;
- a complete evidence payload is rendered incorrectly or incompletely.

No general runtime change was justified from the sampled evidence alone.

## Principal engineering conclusion

The largest remaining accuracy opportunity is complete answer construction under high obligation density. Obligation-level evidence resolution is strong, but the final language model can omit a value, mark supplied evidence unavailable, or compare incomplete operands.
