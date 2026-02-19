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

# In production, keep this list in config and update as you add models.
# This prevents path traversal attacks where users supply "../../../etc/passwd"
ALLOWED_MODELS = {
    "revenue_forecast",
    "churn_model",
    "growth_projection",
    # Add your models here
}

def run_pel_model(model_name, params=None, mode="deterministic", seed=42):
    """Run PEL model with optional parameter overrides.
    
    Security: Validates model_name against allowlist and ensures path stays within MODEL_DIR.
    """
    
    # Enforce an allowlist of known models
    if model_name not in ALLOWED_MODELS:
        raise ValueError(f"Model {model_name} is not allowed")
    
    # Safely construct and validate the model path to prevent traversal
    model_path = os.path.join(MODEL_DIR, f"{model_name}.ir.json")
    model_dir_abs = os.path.abspath(MODEL_DIR)
    model_path_abs = os.path.abspath(model_path)
    
    # Ensure path stays within MODEL_DIR (prevents ../../../etc/passwd attacks)
    if os.path.commonpath([model_dir_abs, model_path_abs]) != model_dir_abs:
        raise ValueError("Invalid model path")
    
    if not os.path.exists(model_path_abs):
        raise ValueError(f"Model {model_name} not found")
    
    cmd = [
        "pel", "run", model_path_abs,
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
    """List available models (from allowlist)."""
    return jsonify({"models": list(ALLOWED_MODELS)})

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

## Advanced Deployment Patterns

### Blue-Green Deployment

Run two identical production environments (blue and green). Deploy new model version to inactive environment, then switch traffic.

```yaml
# deploy.yml
name: Blue-Green Deployment

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Compile Model
        run: pel compile model.pel -o model.ir.json
      
      - name: Deploy to Green Environment
        run: |
          scp model.ir.json server@green-env:/opt/pel/models/
          ssh server@green-env 'systemctl restart pel-service'
      
      - name: Smoke Test Green
        run: |
          curl https://green-env.example.com/health
          curl https://green-env.example.com/api/forecast | jq '.revenue[12]'
      
      - name: Switch Traffic to Green
        run: |
          # Update load balancer
          aws elbv2 modify-target-group \
            --target-group-arn $TG_ARN \
            --targets Id=green-server
      
      - name: Monitor for 10 minutes
        run: |
          sleep 600
          # Check error rates
          if [[ $(check_error_rate) -gt 1% ]]; then
            echo "High error rate, rolling back"
            aws elbv2 modify-target-group \
              --target-group-arn $TG_ARN \
              --targets Id=blue-server
            exit 1
          fi
      
      - name: Decommission Blue
        run: ssh server@blue-env 'systemctl stop pel-service'
```

### Canary Releases

Deploy to small percentage of traffic first:

```yaml
# canary-deploy.yml
name: Canary Deployment

jobs:
  canary:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Canary (10% traffic)
        run: |
          kubectl set image deployment/pel-service \
            pel-service=pel:v2.0.0 \
            --record
          
          kubectl scale deployment/pel-service-canary --replicas=1
          kubectl scale deployment/pel-service-stable --replicas=9
      
      - name: Monitor Canary for 1 hour
        run: |
          sleep 3600
          
          # Check metrics
          ERROR_RATE=$(prometheus_query 'error_rate{deployment="canary"}')
          LATENCY_P99=$(prometheus_query 'latency_p99{deployment="canary"}')
          
          if [[ $ERROR_RATE > 0.01 || $LATENCY_P99 > 500 ]]; then
            echo "Canary metrics poor, rolling back"
            kubectl scale deployment/pel-service-canary --replicas=0
            exit 1
          fi
      
      - name: Promote Canary to 50%
        run: |
          kubectl scale deployment/pel-service-canary --replicas=5
          kubectl scale deployment/pel-service-stable --replicas=5
      
      - name: Monitor for 1 hour
        run: sleep 3600
      
      - name: Full Rollout
        run: |
          kubectl scale deployment/pel-service-canary --replicas=10
          kubectl scale deployment/pel-service-stable --replicas=0
```

### Feature Flags

Toggle model features without redeployment:

```pel
model FeatureFlaggedModel {
  param use_new_retention_model: Boolean = false {
    source: "feature_flags",
    method: "config",
    confidence: 1.0,
    notes: "Toggle for new retention curve calculation"
  }
  
  var retention_rate: Fraction = if use_new_retention_model
    then new_retention_logic()
    else old_retention_logic()
  
  // ...
}
```

Control via configuration:
```bash
# Enable new model for 10% of users
pel run model.ir.json \
  --set use_new_retention_model=$(randomly_true_10_percent)
```

## Monitoring and Observability

### Structured Logging

```python
# pel_service.py
import logging
import json
from datetime import datetime

logger = logging.getLogger('pel_service')

def run_model(model_path, params):
    start_time = datetime.now()
    
    logger.info(json.dumps({
        'event': 'model_execution_start',
        'model': model_path,
        'params': params,
        'timestamp': start_time.isoformat()
    }))
    
    try:
        result = pel.run(model_path, params)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(json.dumps({
            'event': 'model_execution_success',
            'model': model_path,
            'duration_seconds': duration,
            'output_summary': {
                'revenue_t12': result['revenue'][12],
                'constraints_passed': len(result['constraints_passed']),
                'constraints_violated': len(result['constraints_violated'])
            },
            'timestamp': datetime.now().isoformat()
        }))
        
        return result
    
    except Exception as e:
        logger.error(json.dumps({
            'event': 'model_execution_error',
            'model': model_path,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }))
        raise
```

### Prometheus Metrics

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Counters
model_executions_total = Counter(
    'pel_model_executions_total',
    'Total number of model executions',
    ['model_name', 'status']
)

constraint_violations_total = Counter(
    'pel_constraint_violations_total',
    'Total constraint violations',
    ['model_name', 'constraint_name']
)

# Histograms
model_execution_duration = Histogram(
    'pel_model_execution_duration_seconds',
    'Model execution duration',
    ['model_name', 'mode']
)

# Gauges
last_forecast_value = Gauge(
    'pel_last_forecast_value',
    'Last forecasted value',
    ['model_name', 'variable', 'time_step']
)

def track_execution(model_name, mode, result):
    model_executions_total.labels(
        model_name=model_name,
        status='success'
    ).inc()
    
    model_execution_duration.labels(
        model_name=model_name,
        mode=mode
    ).observe(result['execution_time'])
    
    for constraint in result.get('constraints_violated', []):
        constraint_violations_total.labels(
            model_name=model_name,
            constraint_name=constraint['name']
        ).inc()
    
    # Track forecast values
    last_forecast_value.labels(
        model_name=model_name,
        variable='revenue',
        time_step='12'
    ).set(result['variables']['revenue']['time_series'][12])
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "PEL Model Monitoring",
    "panels": [
      {
        "title": "Model Execution Rate",
        "targets": [
          {
            "expr": "rate(pel_model_executions_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Execution Duration (P99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, pel_model_execution_duration_seconds_bucket)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Constraint Violations (Last Hour)",
        "targets": [
          {
            "expr": "sum(increase(pel_constraint_violations_total[1h])) by (constraint_name)"
          }
        ],
        "type": "bar"
      },
      {
        "title": "Revenue Forecast Trend",
        "targets": [
          {
            "expr": "pel_last_forecast_value{variable='revenue', time_step='12'}"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: pel_alerts
    rules:
      - alert: HighConstraintViolationRate
        expr: |
          rate(pel_constraint_violations_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High constraint violation rate"
          description: "Model {{ $labels.model_name }} has {{ $value }} violations/sec"
      
      - alert: ModelExecutionSlow
        expr: |
          histogram_quantile(0.99,
            pel_model_execution_duration_seconds_bucket
          ) > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Model execution slow"
          description: "P99 latency is {{ $value }} seconds"
      
      - alert: ModelExecutionFailing
        expr: |
          rate(pel_model_executions_total{status="error"}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Model executions failing"
          description: "Error rate: {{ $value }} executions/sec"
```

## Scaling Strategies

### Horizontal Scaling (Kubernetes)

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pel-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pel-service
  template:
    metadata:
      labels:
        app: pel-service
    spec:
      containers:
      - name: pel-service
        image: pel:v2.0.0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: PEL_WORKERS
          value: "4"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pel-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pel-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Caching Results

```python
# cache.py
import hashlib
import json
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def cache_key(model_path, params):
    """Generate cache key from model + params"""
    content = f"{model_path}:{json.dumps(params, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()

def get_cached_result(model_path, params):
    key = cache_key(model_path, params)
    cached = redis_client.get(key)
    
    if cached:
        return json.loads(cached)
    return None

def cache_result(model_path, params, result, ttl=3600):
    """Cache result for ttl seconds (default 1 hour)"""
    key = cache_key(model_path, params)
    redis_client.setex(
        key,
        ttl,
        json.dumps(result)
    )

def run_model_cached(model_path, params):
    # Check cache first
    cached = get_cached_result(model_path, params)
    if cached:
        logger.info(f"Cache hit for {model_path}")
        return cached
    
    # Cache miss: execute model
    logger.info(f"Cache miss for {model_path}, executing...")
    result = pel.run(model_path, params)
    
    # Store in cache
    cache_result(model_path, params, result)
    
    return result
```

### Async Task Queues

For long-running Monte Carlo simulations:

```python
# tasks.py
from celery import Celery
import pel

app = Celery('pel_tasks', broker='redis://localhost:6379')

@app.task
def run_monte_carlo(model_path, samples, request_id):
    """Run Monte Carlo simulation async"""
    result = pel.run(
        model_path,
        mode='monte_carlo',
        samples=samples
    )
    
    # Store result
    store_result(request_id, result)
    
    # Notify completion
    send_notification(request_id, status='complete')
    
    return result

# API endpoint
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/forecast/async', methods=['POST'])
def forecast_async():
    request_id = generate_request_id()
    
    # Queue task
    task = run_monte_carlo.delay(
        model_path='model.ir.json',
        samples=10000,
        request_id=request_id
    )
    
    return jsonify({
        'request_id': request_id,
        'task_id': task.id,
        'status': 'queued',
        'status_url': f'/api/status/{request_id}'
    }), 202

@app.route('/api/status/<request_id>')
def check_status(request_id):
    status = get_task_status(request_id)
    return jsonify(status)
```

## Security Best Practices

### Input Validation

```python
# validation.py
from jsonschema import validate, ValidationError

PARAM_SCHEMA = {
    "type": "object",
    "properties": {
        "initial_customers": {
            "type": "number",
            "minimum": 0,
            "maximum": 1000000
        },
        "growth_rate": {
            "type": "number",
            "minimum": -1.0,
            "maximum": 10.0
        }
    },
    "required": ["initial_customers", "growth_rate"]
}

def validate_params(params):
    try:
        validate(instance=params, schema=PARAM_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid parameters: {e.message}")
    
    return True

# In API
@app.route('/api/forecast', methods=['POST'])
def forecast():
    params = request.json
    
    # Validate inputs
    try:
        validate_params(params)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    result = pel.run('model.ir.json', params)
    return jsonify(result)
```

### Rate Limiting

```python
# rate_limit.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/forecast', methods=['POST'])
@limiter.limit("10 per minute")
def forecast():
    # ... implementation
    pass
```

### API Authentication

```python
# auth.py
from functools import wraps
from flask import request, jsonify
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Verify JWT token
            payload = jwt.decode(
                token.replace('Bearer ', ''),
                SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/forecast', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def forecast():
    # ... implementation
    pass
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/pel-models"
DATE=$(date +%Y-%m-%d)

# Backup models
mkdir -p "$BACKUP_DIR/$DATE"
cp -r /opt/pel/models/* "$BACKUP_DIR/$DATE/"

# Backup configuration
cp /etc/pel/config.yml "$BACKUP_DIR/$DATE/"

# Compress
tar -czf "$BACKUP_DIR/pel-backup-$DATE.tar.gz" "$BACKUP_DIR/$DATE"

# Upload to S3
aws s3 cp "$BACKUP_DIR/pel-backup-$DATE.tar.gz" \
  s3://company-backups/pel/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

Schedule with cron:
```cron
0 2 * * * /opt/scripts/backup.sh
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

VERSION=$1  # e.g., v2.0.0

if [ -z "$VERSION" ]; then
  echo "Usage: ./rollback.sh <version>"
  exit 1
fi

echo "Rolling back to $VERSION..."

# Stop service
systemctl stop pel-service

# Restore model from Git
git checkout "$VERSION" model.pel
pel compile model.pel -o /opt/pel/models/model.ir.json

# Restart service
systemctl start pel-service

# Verify health
sleep 5
curl -f http://localhost:8000/health || {
  echo "Health check failed, rolling back failed"
  exit 1
}

echo "Rollback to $VERSION complete"
```

## Practice Exercises

### Exercise 1: Create GitHub Actions CI

Write a GitHub Actions workflow that:
1. Compiles the model
2. Runs deterministic mode
3. Checks no constraints violated
4. Uploads IR as artifact

<details>
<summary>Solution</summary>

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PEL
        run: pip install pel-lang
      
      - name: Compile Model
        run: pel compile model.pel -o model.ir.json
      
      - name: Run Deterministic
        run: |
          pel run model.ir.json --mode deterministic -o results.json
      
      - name: Check Constraints
        run: |
          VIOLATIONS=$(cat results.json | jq '.constraints_violated | length')
          if [ "$VIOLATIONS" -gt 0 ]; then
            echo "ERROR: $VIOLATIONS constraints violated"
            cat results.json | jq '.constraints_violated'
            exit 1
          fi
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: model-ir
          path: model.ir.json
```
</details>

### Exercise 2: Add Prometheus Metrics

Instrument a Flask API with Prometheus metrics for model execution.

<details>
<summary>Solution</summary>

```python
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest
import pel
import time

app = Flask(__name__)

# Metrics
executions = Counter('model_executions_total', 'Total executions', ['status'])
duration = Histogram('model_execution_duration_seconds', 'Execution duration')

@app.route('/api/forecast', methods=['POST'])
def forecast():
    start = time.time()
    
    try:
        params = request.json
        result = pel.run('model.ir.json', params)
        
        executions.labels(status='success').inc()
        duration.observe(time.time() - start)
        
        return jsonify(result)
    
    except Exception as e:
        executions.labels(status='error').inc()
        return jsonify({'error': str(e)}), 500

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(port=8000)
```
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
