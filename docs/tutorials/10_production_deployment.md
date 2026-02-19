# Tutorial 10: Production Deployment

## Overview

Moving PEL models from development to **production** requires versioning, testing, CI/CD, and monitoring. This tutorial shows how to:

- Version models with Git
- Set up automated testing
- Build CI/CD pipelines
- Deploy models as APIs
- Monitor model performance
- Handle model updates safely

**Time required**: 35 minutes  
**Prerequisites**: Tutorials 1-9, Git basics, CI/CD familiarity  
**Learning outcomes**: 
- Version control PEL models
- Write model tests
- Configure GitHub Actions CI/CD
- Deploy models to production
- Update models safely

## Why Production Deployment Matters

### The Spreadsheet Problem: No Deployment Story

Typical spreadsheet "deployment":
```
1. Email "Q1_Budget_Model_FINAL_v3.xlsx" to CFO
2. CFO edits locally, emails back "Q1_Budget_Model_REVIEWED.xlsx"
3. Analyst integrates changes, creates "Q1_Budget_Model_APPROVED.xlsx"
4. Someone finds error, creates "Q1_Budget_Model_APPROVED_FIXED.xlsx"
5. Nobody knows which version is "truth"
```

**Problems**:
- No version history
- No automated testing
- No rollback capability
- No audit trail
- Manual, error-prone process

### The PEL Approach: Software Engineering Best Practices

```
1. Develop model in feature branch
2. Write tests (constraints, edge cases)
3. Open Pull Request
4. CI runs: compile, test, lint
5. Peer review + approval
6. Merge to main
7. CI deploys to staging
8. Validate in staging
9. Promote to production
10. Git tag as v1.2.0
```

**Benefits**:
- Full version history (Git)
- Automated testing (CI)
- Rollback in seconds (Git revert)
- Complete audit trail (commits, PRs)
- Reproducible builds

## Step 1: Version Control with Git

### Initialize Git Repository

```bash
# Create repo
mkdir my-pel-models
cd my-pel-models
git init

# Create directory structure
mkdir -p models tests docs

# Add .gitignore
cat > .gitignore << 'EOF'
# PEL build artifacts
*.ir.json
results*.json
*.html

# Python cache
__pycache__/
*.pyc

# IDE
.vscode/
.idea/

# OS
.DS_Store
EOF

# Initial commit
git add .gitignore
git commit -m "chore: initialize PEL model repository"
```

### Organize Models

```
my-pel-models/
├── models/
│   ├── revenue_forecast.pel      # Production models
│   ├── hiring_plan.pel
│   └── cash_flow.pel
├── tests/
│   ├── test_revenue_forecast.py  # Model tests
│   └── test_cash_flow.py
├── docs/
│   ├── assumptions.md             # Documentation
│   └── changelog.md
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD config
├── .gitignore
└── README.md
```

### Commit Model

```bash
# Add model file
cat > models/revenue_forecast.pel << 'EOF'
model RevenueForecasting {
  param initial_mrr: Currency<USD> = $50_000 {
    source: "billing_system",
    method: "observed",
    confidence: 0.95
  }
  
  param growth_rate: Rate per Month = 0.15 / 1mo {
    source: "historical_analysis",
    method: "fitted",
    confidence: 0.75
  }
  
  var mrr: TimeSeries<Currency<USD>>
  mrr[0] = initial_mrr
  mrr[t+1] = mrr[t] * (1 + growth_rate)
  
  constraint positive_growth {
    mrr[t+1] > mrr[t]
      with severity(warning)
      with message("Revenue declining at t={t}")
  }
}
EOF

# Commit
git add models/revenue_forecast.pel
git commit -m "feat: add revenue forecasting model

- Initial MRR: $50K (from Stripe)
- Growth rate: 15%/mo (fitted from 12mo history)
- Includes growth constraint
"
```

### Semantic Versioning

Use [Semantic Versioning](https://semver.org/) for model releases:

```
v1.2.3
│ │ │
│ │ └─ Patch: Bug fixes, doc updates (backward compatible)
│ └─── Minor: New features, new parameters (backward compatible)
└───── Major: Breaking changes (parameter removal, type changes)
```

**Examples**:
- `v1.0.0`: Initial production release
- `v1.1.0`: Add new `churn_rate` parameter (non-breaking)
- `v1.1.1`: Fix typo in constraint message (patch)
- `v2.0.0`: Change `growth_rate` from monthly to annual (**breaking**)

```bash
# Tag a release
git tag -a v1.0.0 -m "Release v1.0.0: Initial revenue forecast model"
git push origin v1.0.0
```

## Step 2: Automated Testing

### Test Types

| Test Type | Purpose | Example |
|-----------|---------|---------|
| **Compilation** | Model syntax is valid | `pel compile model.pel` succeeds |
| **Constraint** | Business rules hold | Constraints don't trigger fatal errors |
| **Deterministic** | Reproducible results | Same seed → same output |
| **Edge cases** | Handles extremes | Zero revenue, negative growth, etc. |
| **Regression** | No unintended changes | Output matches baseline |

### Example: Pytest Test Suite

```python
# tests/test_revenue_forecast.py

import json
import subprocess
import pytest

def compile_model(model_path):
    """Compile PEL model and return IR path."""
    result = subprocess.run(
        ["pel", "compile", model_path],
        capture_output=True,
        text=True,
        check=True
    )
    # Assumes output is <model>.ir.json
    return model_path.replace(".pel", ".ir.json")

def run_model(ir_path, mode="deterministic", seed=42, steps=12):
    """Run PEL model and return results."""
    result = subprocess.run(
        [
            "pel", "run", ir_path,
            "--mode", mode,
            "--seed", str(seed),
            "--steps", str(steps),
            "-o", "test_output.json"
        ],
        capture_output=True,
        text=True,
        check=True
    )
    
    with open("test_output.json") as f:
        return json.load(f)

class TestRevenueForecasting:
    """Test suite for revenue_forecast.pel"""
    
    @pytest.fixture
    def model_ir(self):
        """Compile model once for all tests."""
        return compile_model("models/revenue_forecast.pel")
    
    def test_compilation(self):
        """Model compiles without errors."""
        ir_path = compile_model("models/revenue_forecast.pel")
        assert ir_path.endswith(".ir.json")
    
    def test_deterministic_reproducibility(self, model_ir):
        """Same seed produces same results."""
        results1 = run_model(model_ir, seed=42)
        results2 = run_model(model_ir, seed=42)
        
        assert results1 == results2
    
    def test_growth_constraint(self, model_ir):
        """Revenue growth constraint holds."""
        results = run_model(model_ir, steps=12)
        
        mrr_values = [r["value"] for r in results["mrr"]]
        
        # Check monotonic increase
        for i in range(len(mrr_values) - 1):
            assert mrr_values[i+1] > mrr_values[i], \
                f"Revenue declined: {mrr_values[i]} -> {mrr_values[i+1]}"
    
    def test_initial_condition(self, model_ir):
        """Initial MRR matches parameter."""
        results = run_model(model_ir)
        
        initial_mrr = results["mrr"][0]["value"]
        assert initial_mrr == 50_000, \
            f"Initial MRR mismatch: {initial_mrr} != 50,000"
    
    def test_12_month_projection(self, model_ir):
        """12-month projection is reasonable."""
        results = run_model(model_ir, steps=12)
        
        mrr_month_12 = results["mrr"][12]["value"]
        
        # With 15% monthly growth: 50K * 1.15^12 ≈ $267K
        expected = 50_000 * (1.15 ** 12)
        
        assert abs(mrr_month_12 - expected) < 1000, \
            f"Month 12 projection: {mrr_month_12} vs expected {expected}"
    
    def test_edge_case_zero_growth(self):
        """Model handles zero growth."""
        # Create variant with zero growth
        # (In practice, use parameterized model or CLI override)
        # For now, test that compilation succeeds
        pass  # Placeholder
    
    def test_no_fatal_constraints(self, model_ir):
        """No fatal constraint violations."""
        results = run_model(model_ir)
        
        assert results["status"] != "constraint_violation", \
            f"Fatal constraint triggered: {results.get('message')}"
```

### Run Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest tests/ -v

# Output:
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_compilation PASSED
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_deterministic_reproducibility PASSED
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_growth_constraint PASSED
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_initial_condition PASSED
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_12_month_projection PASSED
# tests/test_revenue_forecast.py::TestRevenueForecasting::test_no_fatal_constraints PASSED
# ==================== 6 passed in 2.34s ====================
```

## Step 3: CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml

name: PEL Model CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-compile:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install PEL
        run: |
          pip install pel-lang
      
      - name: Compile all models
        run: |
          for model in models/*.pel; do
            echo "Compiling $model..."
            pel compile "$model" || exit 1
          done
      
      - name: Lint models (future)
        run: |
          # When `pel lint` ships
          # pel lint models/*.pel
          echo "Linting not yet available"
  
  test:
    runs-on: ubuntu-latest
    needs: lint-and-compile
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pel-lang pytest
      
      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test_output.json
  
  deploy-staging:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install PEL
        run: |
          pip install pel-lang
      
      - name: Compile models
        run: |
          mkdir -p build
          for model in models/*.pel; do
            pel compile "$model"
            mv "${model%.pel}.ir.json" build/
          done
      
      - name: Deploy to staging
        run: |
          # Upload IR files to staging environment
          # (AWS S3, GCS, internal server, etc.)
          echo "Deploying to staging..."
          # aws s3 sync build/ s3://my-pel-models-staging/
      
      - name: Create release artifact
        uses: actions/upload-artifact@v3
        with:
          name: compiled-models
          path: build/*.ir.json
```

### Branch Strategy

```
main (production)
  ├── v1.0.0 (tag)
  ├── v1.1.0 (tag)
  └── HEAD
  
develop (pre-production)
  └── feature/add-churn-model (feature branches)
  └── feature/update-growth-assumptions
```

**Workflow**:
1. Create feature branch: `git checkout -b feature/add-churn-model`
2. Develop + test locally
3. Push + open PR to `develop`
4. CI runs on PR
5. Review + merge to `develop`
6. Test in staging environment
7. Promote: merge `develop` → `main`
8. Tag release: `git tag v1.2.0`
9. CI deploys to production

## Step 4: Model Deployment

### Deployment Targets

| Target | Use Case | How to Deploy |
|--------|----------|---------------|
| **Local** | Development, testing | Run `pel run` directly |
| **Batch jobs** | Monthly forecasts, reports | Cron job or scheduler |
| **API** | Real-time predictions | Flask/FastAPI wrapper |
| **Data pipeline** | ETL integration | Airflow/Prefect task |
| **Notebook** | Analysis, exploration | Jupyter with PEL kernel |

### Example: Deploy as REST API

```python
# api/model_server.py

from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

MODEL_DIR = os.environ.get("MODEL_DIR", "./models")

def run_pel_model(model_name, params=None, mode="deterministic", seed=42):
    """Run PEL model with optional parameter overrides."""
    
    model_path = f"{MODEL_DIR}/{model_name}.ir.json"
    
    if not os.path.exists(model_path):
        raise ValueError(f"Model {model_name} not found")
    
    cmd = [
        "pel", "run", model_path,
        "--mode", mode,
        "--seed", str(seed),
        "-o", "/tmp/pel_output.json"
    ]
    
    # TODO: Add parameter override support when CLI supports it
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Model execution failed: {result.stderr}")
    
    with open("/tmp/pel_output.json") as f:
        return json.load(f)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/models', methods=['GET'])
def list_models():
    """List available models."""
    models = [
        f.replace(".ir.json", "")
        for f in os.listdir(MODEL_DIR)
        if f.endswith(".ir.json")
    ]
    return jsonify({"models": models})

@app.route('/models/<model_name>/run', methods=['POST'])
def run_model(model_name):
    """Run model with parameters."""
    
    data = request.json or {}
    mode = data.get("mode", "deterministic")
    seed = data.get("seed", 42)
    
    try:
        results = run_pel_model(model_name, mode=mode, seed=seed)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**Deploy**:

```bash
# Build Docker image
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

RUN pip install pel-lang flask

COPY models/ /app/models/
COPY api/ /app/api/

WORKDIR /app
ENV MODEL_DIR=/app/models

EXPOSE 8000
CMD ["python", "api/model_server.py"]
EOF

# Build and run
docker build -t pel-model-server .
docker run -p 8000:8000 pel-model-server

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/models/revenue_forecast/run \
  -H "Content-Type: application/json" \
  -d '{"mode": "deterministic", "seed": 42}'
```

## Step 5: Monitoring & Observability

### Metrics to Track

| Metric | What | Why |
|--------|------|-----|
| **Execution time** | How long models take to run | Detect performance degradation |
| **Constraint violations** | Rate of fatal/warning constraints | Model health indicator |
| **Parameter drift** | Changes in calibrated parameters over time | Detect regime changes |
| **Prediction error** | Actual vs predicted (when available) | Model accuracy |
| **API latency** | Response time for model API | User experience |

### Example: Logging Model Execution

```python
# utils/model_logger.py

import logging
import json
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pel_model")

class ModelExecutionLogger:
    """Log PEL model executions for monitoring."""
    
    def __init__(self, model_name, version):
        self.model_name = model_name
        self.version = version
    
    def log_execution(self, mode, seed, duration_sec, status, results=None):
        """Log model execution metrics."""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": self.model_name,
            "version": self.version,
            "mode": mode,
            "seed": seed,
            "duration_sec": duration_sec,
            "status": status
        }
        
        if results and "warnings" in results:
            log_entry["warnings"] = len(results["warnings"])
        
        logger.info(json.dumps(log_entry))
    
    def log_constraint_violation(self, constraint_name, message):
        """Log constraint violation."""
        logger.warning(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "model": self.model_name,
            "event": "constraint_violation",
            "constraint": constraint_name,
            "message": message
        }))

# Usage in API
log = ModelExecutionLogger("revenue_forecast", "v1.2.0")

start = time.time()
results = run_pel_model("revenue_forecast", mode="deterministic", seed=42)
duration = time.time() - start

log.log_execution(
    mode="deterministic",
    seed=42,
    duration_sec=duration,
    status="success",
    results=results
)
```

### Alerting

```yaml
# alerting/rules.yml (Prometheus-style)

groups:
  - name: pel_models
    interval: 1m
    rules:
      - alert: HighConstraintViolationRate
        expr: rate(pel_constraint_violations_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High constraint violation rate for {{ $labels.model }}"
      
      - alert: ModelExecutionSlow
        expr: pel_execution_duration_seconds > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Model {{ $labels.model }} taking >30s to execute"
      
      - alert: ModelExecutionFailed
        expr: rate(pel_execution_failures_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Model {{ $labels.model }} failing >5% of executions"
```

## Step 6: Safe Model Updates

### Update Workflow

```
1. Develop new version (feature branch)
2. Run A/B test (old vs new model)
3. Compare outputs (deterministic mode)
4. If breaking change: bump major version
5. Deploy to staging
6. Run smoke tests
7. Gradual rollout (10% → 50% → 100% traffic)
8. Monitor for regressions
9. Rollback if issues detected
```

### Example: A/B Testing Models

```python
# Compare two model versions

def compare_models(model_v1_ir, model_v2_ir, seed=42, steps=12):
    """Compare outputs of two model versions."""
    
    results_v1 = run_pel_model(model_v1_ir, seed=seed, steps=steps)
    results_v2 = run_pel_model(model_v2_ir, seed=seed, steps=steps)
    
    # Compare MRR projections
    mrr_v1 = [r["value"] for r in results_v1["mrr"]]
    mrr_v2 = [r["value"] for r in results_v2["mrr"]]
    
    diffs = [abs(v1 - v2) / v1 for v1, v2 in zip(mrr_v1, mrr_v2)]
    max_diff = max(diffs)
    
    return {
        "max_diff_pct": max_diff * 100,
        "mrr_v1_final": mrr_v1[-1],
        "mrr_v2_final": mrr_v2[-1],
        "breaking_change": max_diff > 0.05  # >5% difference
    }

# Run comparison
comparison = compare_models("v1.ir.json", "v2.ir.json")

if comparison["breaking_change"]:
    print("⚠️  Breaking change detected - bump major version")
else:
    print("✅ Non-breaking change - safe to deploy")
```

## Production Checklist

Before deploying to production:

- [ ] Model compiles without errors
- [ ] All tests pass (compilation, constraints, edge cases)
- [ ] CI pipeline is green
- [ ] Peer review completed
- [ ] Provenance documentation complete
- [ ] High-confidence parameters ≥70%
- [ ] Low-confidence parameters flagged for monitoring
- [ ] Version tagged (semantic versioning)
- [ ] Deployment tested in staging
- [ ] Rollback plan documented
- [ ] Monitoring/alerting configured
- [ ] API documentation updated (if applicable)

## Quiz: Test Your Understanding

1. **What's the purpose of deterministic testing?**
   <details>
   <summary>Answer</summary>
   Ensure reproducibility - same seed produces same results every time. Essential for regression testing and debugging.
   </details>

2. **When should you bump the major version (e.g., v1.x.x → v2.0.0)?**
   <details>
   <summary>Answer</summary>
   Breaking changes:
   - Parameter removal
   - Type changes (Currency → Fraction)
   - Formula changes that significantly alter outputs (>5% difference)
   - Constraint severity changes (warning → fatal)
   </details>

3. **What's the benefit of Git over email for model distribution?**
   <details>
   <summary>Answer</summary>
   - Full version history (who changed what, when)
   - Branching/merging (parallel development)
   - Rollback (revert to any previous version)
   - Audit trail (commit messages)
   - No "FINAL_v3" file naming chaos
   </details>

4. **Why run models in staging before production?**
   <details>
   <summary>Answer</summary>
   Catch issues in production-like environment:
   - Performance problems
   - Resource constraints
   - Integration bugs
   - Unexpected constraint violations
   
   Without risking production systems.
   </details>

## Key Takeaways

1. **Use Git for version control**: Commit models, not Excel files
2. **Automate testing**: CI catches errors before production
3. **Semantic versioning**: v1.2.3 = major.minor.patch
4. **Deploy safely**: Staging → smoke tests → gradual rollout
5. **Monitor in production**: Track execution time, constraint violations, accuracy

## Next Steps

- **Practice**: Set up a Git repo for your PEL models
- **Experiment**: Build a CI/CD pipeline with GitHub Actions
- **Explore**: Deploy a model as an API using Flask
- **Reference**: See `/docs/deployment/` for advanced patterns

## Additional Resources

- [CI/CD Examples](/docs/deployment/ci_cd_examples.md)
- [Docker Deployment Guide](/docs/deployment/docker.md)
- [Monitoring Best Practices](/docs/deployment/monitoring.md)
- [Rollback Strategies](/docs/deployment/rollback.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
