# Performance Suite

## What this suite measures

- Microbenchmarks (ops/sec, allocations/op)
- Macrobenchmarks (service-like and serialization/database stubs)
- Real-world hooks (compile/build/sample app tasks)

## Required outputs

Emit `<outdir>/suite.performance.json` with:

- `suite`: `performance`
- `status`: `pass|fail`
- `metrics.latency_ms.p50|p95|p99`
- `metrics.throughput_ops_per_sec`
- `metrics.rss_mb`
- `metrics.startup_ms`
- `artifacts.latency_histogram`
- `artifacts.log`

## How to add a workload

1. Add workload docs under `workloads/*`.
2. Add runnable hook in `run_suite.sh performance` branch.
3. Emit measurements in canonical shape.
