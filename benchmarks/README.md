# Benchmarks

This directory contains PEL benchmark inputs, scripts, and generated results.

---

## Included Artifacts

- `pel_100/` — PEL-100 benchmark model set
- `score_benchmark.py` — benchmark scoring script
- `PEL_100_RESULTS.json` — machine-readable benchmark results
- `PEL_100_RESULTS.md` — human-readable benchmark summary

---

## Run Benchmark Scoring

From repository root:

```bash
python3 benchmarks/score_benchmark.py
```

---

## View Results

```bash
cat benchmarks/PEL_100_RESULTS.md
```

---

## Notes

- Keep benchmark output files deterministic where feasible (seeded runs).
- Update both JSON and Markdown result artifacts when refreshing benchmarks.
- If benchmark schema changes, document it in PR notes and update consumer scripts.
