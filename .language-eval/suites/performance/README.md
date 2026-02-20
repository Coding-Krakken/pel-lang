# Performance Suite

## What this suite measures

- Microbenchmarks (ops/sec, allocations/op)
- Macrobenchmarks (service-like and serialization/database stubs)
- Real-world hooks (compile/build/sample app tasks)

## Required outputs

Emit `<outdir>/suite.performance.json` with:

- `suite`: `performance`
- `status`: `pass|fail|skip`
- `metrics.latency_ms.p50|p95|p99`
- `metrics.throughput_ops_per_sec`
- `metrics.rss_mb`
- `metrics.startup_ms`
- `artifacts.latency_histogram`
- `artifacts.log`

## Performance Targets (SLA)

| Milestone | Target Time | Notes |
|-----------|------------|-------|
| Micro benchmarks (warmup=1, repeat=3) | 2-5 minutes | Quick validation |
| Standard (warmup=1, repeat=5) | 10-15 minutes | Default --repeat setting |
| Full suite (warmup=3, repeat=10) | 30-45 minutes | Deep characterization |
| Timeout | 60 minutes | Hard limit per benchmark |

**Memory:** < 1 GB peak RSS for typical workload (vary by language)

**Determinism:** Same hardware should produce ±3% variance. If >5% variance: investigate environment (power mgmt, background processes).

## How to add a workload

1. Add workload docs under `workloads/*`.
2. Add runnable hook in `run_suite.sh performance` branch.
3. Emit measurements in canonical shape.

**Warmup guidance:**
- Interpreters/VMs: >=3 warmup runs recommended
- Compiled languages: 1 warmup usually sufficient
- Configure via `--warmup` flag
