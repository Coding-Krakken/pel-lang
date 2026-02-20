# Human Factors Suite

## What this suite measures

- Time-to-fix task templates
- Comprehension/maintainability checklists
- Reproducible study protocol (manual or scripted)

## Output contract

At minimum emit `<outdir>/suite.human_factors.json` with:

- `suite`: `human_factors`
- `status`: `pass|fail`
- `metrics.checklist_coverage`
- `metrics.tasks_defined`
- `artifacts.log`

## Study template

- Define participant profile
- Define tasks and success criteria
- Record time-to-completion and error count
- Summarize blockers and remediation ideas
