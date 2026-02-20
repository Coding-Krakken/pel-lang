# Human Factors Suite

## What this suite measures

- Time-to-fix task templates
- Comprehension/maintainability checklists
- Reproducible study protocol (manual or scripted)

## Output contract

At minimum emit `<outdir>/suite.human_factors.json` with:

- `suite`: `human_factors`
- `status`: `pass|fail|skip`
- `metrics.checklist_coverage`
- `metrics.tasks_defined`
- `artifacts.log`

## Performance Targets (SLA)

| Activity | Target Time | Notes |
|----------|------------|-------|
| Scripted checklist review (5 items) | < 10 minutes | Automated template |
| Documentation audit | 15-30 minutes | Manual review |
| Task timing collection (5 tasks, 1 participant) | 2-3 hours | Human study component |
| Full user study (5 participants, >20 hours) | < 1 week of wall time | Best effort; flexible |
| Timeout (single task) | None | Human-driven; not applicable |

**Measurement Method:**
- Tasks 1-5 should each complete within documented SLAs
- Total time is cumulative + human availability
- Results logged in `artifacts/study_log.json`

## Study template

- Define participant profile
- Define tasks and success criteria
- Record time-to-completion and error count
- Summarize blockers and remediation ideas

**Participant min:** 1 (scripted); 5+ (formal study)

## Artifact Examples

```json
{
  "suite": "human_factors",
  "status": "pass",
  "metrics": {
    "checklist_coverage": 0.85,
    "tasks_defined": 5,
    "tasks_completed": 5,
    "avg_time_to_task_sec": 480,
    "error_count": 2
  },
  "artifacts": {
    "log": "suite.human_factors.log",
    "study_protocol": "protocol.md",
    "raw_timings": {
      "task1": {"time_sec": 180, "errors": 0},
      "task2": {"time_sec": 420, "errors": 1}
    },
    "blockers": [
      {"task": "task2", "blocker": "unclear error message", "severity": "medium"}
    ]
  }
}
```
