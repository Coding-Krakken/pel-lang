# PEL Calibration Module

## Overview

The PEL Calibration module enables data-driven modeling by integrating external data sources, fitting distribution parameters from observations, and detecting model drift. This implements the "Digital Twin" capability that distinguishes PEL from static modeling approaches.

## Features

### CSV Data Connector
- Load CSV files from local filesystem
- Column mapping to PEL parameters
- Type conversion and validation
- Missing value handling (drop, mean, median, forward-fill)
- Outlier detection and filtering (IQR, z-score methods)

### Parameter Estimation
- **Maximum Likelihood Estimation (MLE)** for:
  - Normal distribution
  - LogNormal distribution
  - Beta distribution
- Goodness-of-fit tests:
  - Kolmogorov-Smirnov test
  - AIC/BIC for model comparison
- Confidence intervals (analytical and bootstrap)
- Distribution comparison

### Drift Detection
- **MAPE** (Mean Absolute Percentage Error)
- **RMSE** (Root Mean Squared Error)
- **CUSUM** (Cumulative Sum) changepoint detection
- Configurable thresholds and alerts
- Rolling window analysis

## Installation

The calibration module requires additional dependencies:

```bash
pip install pel-lang[calibration]
```

Or install dependencies manually:
```bash
pip install scipy pandas numpy pyyaml
```

## Quick Start

### 1. Prepare Configuration File

Create a YAML configuration file (`calibration_config.yaml`):

```yaml
csv_path: "data/historical_churn.csv"
model_path: "models/saas_churn.ir.json"
output_path: "results/calibrated"

csv_config:
  encoding: "utf-8"
  delimiter: ","
  column_mapping:
    churn_rate: "monthly_churn_rate"
    customer_lifetime: "avg_lifetime_months"
  type_mapping:
    churn_rate: "float"
    customer_lifetime: "float"
  missing_values:
    strategy: "drop"
  outlier_filtering:
    - column: "churn_rate"
      method: "iqr"
      threshold: 3.0

parameters:
  churn_rate:
    data_column: "churn_rate"
    distribution: "beta"
    use_bootstrap: true
    bootstrap_samples: 1000
  customer_lifetime:
    data_column: "customer_lifetime"
    distribution: "lognormal"

drift_config:
  mape_threshold: 0.15
  cusum_threshold: 5.0
  cusum_slack: 0.5
```

### 2. Run Calibration

Using the CLI:
```bash
pel calibrate calibration_config.yaml
```

Or programmatically:
```python
from runtime.calibration import Calibrator, CalibrationConfig

config = CalibrationConfig.from_yaml('calibration_config.yaml')
calibrator = Calibrator(config)
result = calibrator.calibrate()

print(f"Calibrated {len(result.parameters)} parameters")
print(f"MAPE: {result.drift_reports['churn_rate'].mape:.2%}")
```

### 3. Review Results

Calibration generates three output files:

1. **Calibrated Model** (`calibrated_calibrated.ir.json`): Updated model with fitted parameters
2. **JSON Report** (`calibrated_report.json`): Machine-readable results
3. **Markdown Report** (`calibrated_report.md`): Human-readable summary

## API Documentation

### CSVConnector

```python
from runtime.calibration import CSVConnector

connector = CSVConnector()

# Load and prepare data
df = connector.load_and_prepare(
    csv_path=Path('data.csv'),
    config={
        'column_mapping': {'param1': 'col1'},
        'type_mapping': {'param1': 'float'},
        'missing_values': {'strategy': 'drop'},
    }
)

# Extract column for fitting
data = connector.extract_column(df, 'param1')
```

### ParameterEstimator

```python
from runtime.calibration import ParameterEstimator
import numpy as np

estimator = ParameterEstimator()

# Fit single distribution
data = np.random.normal(10, 2, 1000)
result = estimator.fit_normal(data)

print(f"Mean: {result.parameters['mean']:.2f}")
print(f"Std: {result.parameters['std']:.2f}")
print(f"AIC: {result.aic:.2f}")
print(f"KS p-value: {result.ks_pvalue:.4f}")

# Compare multiple distributions
results = estimator.compare_distributions(data, ['normal', 'lognormal'])
best_fit = list(results.keys())[0]  # Sorted by AIC
```

### DriftDetector

```python
from runtime.calibration import DriftDetector
import numpy as np

detector = DriftDetector(mape_threshold=0.15)

observed = np.array([100, 105, 102, 98, 150, 155, 160])
predicted = np.array([100, 100, 100, 100, 100, 100, 100])

report = detector.detect_drift(observed, predicted)

print(f"MAPE: {report.mape:.2%}")
print(f"CUSUM detected: {report.cusum_detected}")
print(f"Changepoint: {report.cusum_changepoint}")

for rec in report.recommendations:
    print(f"- {rec}")
```

### Calibrator

```python
from runtime.calibration import Calibrator, CalibrationConfig
from pathlib import Path

config = CalibrationConfig(
    csv_path="data/historical.csv",
    model_path="model.ir.json",
    output_path="results/calibrated",
    parameters={
        'growth_rate': {
            'data_column': 'monthly_growth',
            'distribution': 'normal',
        }
    },
    csv_config={
        'column_mapping': {'monthly_growth': 'growth_pct'},
        'type_mapping': {'monthly_growth': 'float'},
    }
)

calibrator = Calibrator(config)
result = calibrator.calibrate()

# Access fitted parameters
fit = result.parameters['growth_rate']
print(f"Distribution: {fit.distribution}")
print(f"Parameters: {fit.parameters}")
print(f"95% CI: {fit.confidence_intervals}")
```

## Configuration Reference

### CSV Config Options

| Field | Type | Description |
|-------|------|-------------|
| `encoding` | string | File encoding (default: utf-8) |
| `delimiter` | string | Column separator (default: comma) |
| `column_mapping` | dict | Map PEL params to CSV columns |
| `type_mapping` | dict | Column type conversions |
| `missing_values` | dict | Missing value handling config |
| `outlier_filtering` | list | Outlier detection configs |

### Parameter Config Options

| Field | Type | Description |
|-------|------|-------------|
| `data_column` | string | CSV column containing observations |
| `distribution` | string | Distribution type (normal, lognormal, beta) |
| `use_bootstrap` | boolean | Use bootstrap for CI (default: false) |
| `bootstrap_samples` | int | Number of bootstrap samples (default: 1000) |
| `predicted_column` | string | Column with predictions for drift detection |

### Drift Config Options

| Field | Type | Description |
|-------|------|-------------|
| `mape_threshold` | float | MAPE threshold for alerts (default: 0.15) |
| `rmse_threshold` | float | RMSE threshold (optional) |
| `cusum_threshold` | float | CUSUM decision threshold (default: 5.0) |
| `cusum_slack` | float | CUSUM slack parameter (default: 0.5) |

## Examples

See comprehensive examples in:
- `/examples/calibration_saas_churn.pel` + CSV data
- `/examples/calibration_manufacturing.pel` + CSV data
- `/docs/tutorials/calibration.md` (Tutorial 8)

## Limitations (MVP v0.2.0)

- CSV files only (no database/API connectors)
- MLE only (Bayesian methods in v0.3.0)
- Three distributions supported (more in future releases)
- Basic drift detection (advanced methods in v0.3.0)
- No correlation estimation from data

## Roadmap (v0.3.0+)

- QuickBooks, Salesforce, Stripe API connectors
- Bayesian parameter estimation
- Advanced drift detection (changepoint algorithms)
- Database connectors (PostgreSQL, BigQuery)
- Real-time streaming (Kafka integration)
- Correlation matrix estimation

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.

## License

Dual-licensed under AGPL-3.0 and Commercial License.
See [LICENSE](../../LICENSE) and [COMMERCIAL-LICENSE.md](../../COMMERCIAL-LICENSE.md).
