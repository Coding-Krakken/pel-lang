# PEL Calibration Examples

This directory contains worked examples demonstrating PEL's calibration capabilities.

## SaaS Churn Calibration Example

### Files

- `calibration_saas_churn.pel` - PEL model for SaaS customer churn
- `calibration_saas_churn_data.csv` - Historical churn data (14 months)
- `calibration_saas_churn_config.yaml` - Calibration configuration

### Model Description

The SaaS churn model simulates customer acquisition, churn, and revenue over a 12-month period. Key parameters include:

- **Monthly churn rate**: Probability a customer churns each month
- **Average customer lifetime**: How long customers typically stay (in months)
- **Monthly new customers**: New customer acquisitions per month
- **Revenue per customer**: Average monthly revenue per customer

### Calibration Process

The calibration process fits the churn rate and customer lifetime parameters using maximum likelihood estimation (MLE) on historical data.

**Before calibration** (expert estimates):
```yaml
monthly_churn_rate: Beta(alpha: 2, beta: 20)  # ~9% mean, low confidence
avg_customer_lifetime: LogNormal(mu: 2.5, sigma: 0.5)  # ~12 months median
```

**After calibration** (data-driven):
The parameters are fitted to 14 months of actual churn data, with confidence intervals based on bootstrap sampling.

### Running the Example

#### Step 1: Compile the model

```bash
cd /home/obsidian/Projects/PEL
python -m compiler.compiler examples/calibration_saas_churn.pel -o examples/saas_churn.ir.json
```

#### Step 2: Run calibration

```bash
pel calibrate examples/calibration_saas_churn_config.yaml
```

Or programmatically:

```python
from pathlib import Path
from runtime.calibration import Calibrator, CalibrationConfig

config = CalibrationConfig.from_yaml(
    Path('examples/calibration_saas_churn_config.yaml')
)
calibrator = Calibrator(config)
result = calibrator.calibrate()

# View fitted parameters
for param_name, fit in result.parameters.items():
    print(f"{param_name}: {fit.distribution}")
    print(f"  Parameters: {fit.parameters}")
    print(f"  AIC: {fit.aic:.2f}")
    print(f"  KS p-value: {fit.ks_pvalue:.4f}")
```

#### Step 3: Review outputs

Calibration generates three files:

1. **Calibrated Model**: `examples/calibration_saas_churn_calibrated_calibrated.ir.json`
   - Updated model with fitted parameters
   - Includes provenance metadata (source: "calibrated", method: "mle")

2. **JSON Report**: `examples/calibration_saas_churn_calibrated_report.json`
   - Machine-readable results
   - Fitted parameters with confidence intervals
   - Goodness-of-fit statistics (AIC, BIC, KS test)
   - Drift detection results (if applicable)

3. **Markdown Report**: `examples/calibration_saas_churn_calibrated_report.md`
   - Human-readable summary
   - Parameter estimates with 95% confidence intervals
   - Recommendations

#### Step 4: Run calibrated model

```bash
pel run examples/calibration_saas_churn_calibrated_calibrated.ir.json --mode monte_carlo --runs 10000 -o results.json
```

### Expected Results

After calibration with the provided data, you should see:

**Monthly Churn Rate** (Beta distribution):
- alpha ≈ 11.5
- beta ≈ 132
- Mean ≈ 0.080 (8% monthly churn)
- 95% CI: [0.065, 0.095]

**Average Customer Lifetime** (LogNormal distribution):
- mu ≈ 2.61
- sigma ≈ 0.15
- Median ≈ 13.6 months
- 95% CI: [12.8, 14.5]

The calibrated parameters reflect the actual observed churn patterns in the data, with higher confidence than the initial expert estimates.

### Interpreting Results

**Goodness of Fit**:
- **AIC/BIC**: Lower values indicate better fit. Compare across distributions.
- **KS p-value**: p > 0.05 suggests distribution fits data well

**Confidence Intervals**:
- Narrow intervals (relative to parameter value) indicate precise estimates
- Wide intervals suggest more data is needed or high natural variability

**Provenance**:
The calibrated model includes provenance metadata:
```json
"provenance": {
  "source": "calibrated",
  "method": "mle",
  "confidence": 0.85,
  "calibration_timestamp": "2026-02-19T...",
  "aic": 125.3,
  "bic": 128.7
}
```

This tells downstream users that the parameter values are data-driven, not assumptions.

## Data Format Requirements

CSV files should have:
- Header row with column names
- One row per observation
- Numeric columns for quantitative parameters
- No missing values in critical columns (or specify handling strategy)

Valid strategies for missing values:
- `drop`: Remove rows with missing values
- `mean`: Fill with column mean
- `median`: Fill with column median
- `forward_fill`: Forward-fill from previous value
- `fill`: Fill with specific value

## Troubleshooting

**"Column not found" error**:
- Check `column_mapping` in config file
- Verify CSV header matches exactly (case-sensitive)

**"Distribution requires positive data" error**:
- LogNormal requires all values > 0
- Beta requires all values in [0, 1]
- Check data preprocessing and outlier filtering

**Poor goodness-of-fit (low KS p-value)**:
- Try alternative distributions using `compare_distributions`
- Check for outliers or data quality issues
- Consider data transformations

**High MAPE in drift detection**:
- Model may need structural changes, not just parameter updates
- Check for regime changes or seasonality
- Consider rolling calibration with recent data only

## Next Steps

After successful calibration:

1. **Validate** the calibrated model on held-out data
2. **Document** the data sources and calibration process
3. **Schedule** regular recalibration (e.g., quarterly)
4. **Monitor** drift metrics to detect when recalibration is needed
5. **Integrate** calibration into CI/CD pipeline for automated updates

## Additional Examples

See also:
- Manufacturing capacity planning (coming soon)
- Financial forecasting (coming soon)
- Tutorial 8: Complete calibration walkthrough (docs/tutorials/calibration.md)
