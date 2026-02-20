# Glossary

- **Determinism:** same input + environment produce identical outputs.
- **UB (Undefined Behavior):** behavior not defined by specification; results may vary.
- **Tail latency:** high-percentile latency (typically p95/p99) representing worst-case user impact.
- **GC pause:** stop-the-world or mutator-impact interval caused by garbage collection.
- **Soundness:** static analysis/type system property where accepted programs uphold guarantees.
- **Hermetic build:** build isolated from undeclared external state (network/system drift).
- **Conformance:** adherence to language specification and reference behavior.
- **Expected failure:** known failing test recorded with rationale and owner.
- **Baseline:** reference result set used for regression comparison.
- **Regression tolerance:** maximum allowable metric degradation before gate failure.
- **Idempotence (formatter):** formatting output does not change on repeated runs.
- **SAST:** static application security testing.
- **Supply-chain risk:** risk from dependencies, transitive code, and artifact provenance.
- **Warmup:** pre-measurement executions used to stabilize runtime state.
- **Repeat count:** number of measured iterations used for aggregate metrics.
