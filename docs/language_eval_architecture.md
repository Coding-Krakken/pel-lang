# Language Evaluation Framework Architecture

This diagram shows the flow of data and control in the PEL Language Evaluation Framework:

![Architecture Diagram](language_eval_architecture.mmd)

- **User/Contributor**: Runs CLI scripts to evaluate a language implementation.
- **Language Eval Scripts**: Main entry points (scorecard, emit_report, compare_baseline, ci_gate).
- **Scorecard**: Computes weighted scores from normalized results.
- **Emit Report**: Generates human- and machine-readable reports.
- **Compare Baseline**: Detects regressions/deltas against a baseline.
- **CI Gate**: Enforces quality, determinism, and regression gates in CI.
- **Artifacts**: JSON and Markdown files for results, reports, and comparisons.

See the Mermaid diagram in this directory for a visual representation.
