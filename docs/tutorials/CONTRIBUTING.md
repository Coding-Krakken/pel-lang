# Contributing to PEL Tutorials

Thank you for your interest in improving the PEL tutorial suite! This guide will help you create high-quality tutorials that meet our standards.

## Tutorial Quality Standards

All tutorials must:
- ✅ Use **valid PEL types** (Fraction, not Probability; Boolean, not Bool)
- ✅ Include **working, compilable code examples**
- ✅ Have **accurate internal links** (point to existing files)
- ✅ Follow **consistent formatting** (see template below)
- ✅ Include **provenance metadata** in examples
- ✅ Pass **automated validation** (see Testing section)

## Tutorial Structure Template

```markdown
# Tutorial N: Title (Time estimate)

## Overview

Brief description (2-3 sentences) of what this tutorial covers.

**Time required**: XX minutes  
**Prerequisites**: Tutorial 1, Tutorial 2  
**Learning outcomes**: 
- Outcome 1
- Outcome 2
- Outcome 3

## Why This Matters

Real-world motivation (1 paragraph).

## Section 1: Core Concept

### Subsection

Explanation with code example:

\`\`\`pel
model Example {
  param value: Fraction = 0.5 {
    source: "example",
    method: "assumption",
    confidence: 0.90
  }
}
\`\`\`

**Key points**:
- Point 1
- Point 2

## Quiz Questions

<details>
<summary>Question 1?</summary>

Answer explanation.

</details>

## Key Takeaways

1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

## Next Steps

- **Tutorial X**: Next topic
- **Reference**: See `spec/file.md` for details

## Additional Resources

- [Specification](../../spec/relevant_spec.md)
- [Examples](../../examples/)
```

## Type System Rules

### ✅ Correct Types

```pel
param probability_value: Fraction = 0.25      // ✅ Correct
param is_active: Boolean = true               // ✅ Correct
param count: Fraction = 100.0                 // ✅ Correct
var status: TimeSeries<Boolean>               // ✅ Correct
```

### ❌ Invalid Types

```pel
param probability_value: Probability = 0.25   // ❌ Invalid - use Fraction
param is_active: Bool = true                  // ❌ Invalid - use Boolean
# Note: TimeSeries with Bool type parameter is also invalid - use Boolean
```

## Syntax Patterns

### ✅ Correct Syntax

```pel
// Correlation in provenance block
param growth_rate: Rate per Month 
  ~ Normal(μ=0.15/1mo, σ=0.05/1mo) {
    source: "forecast",
    method: "assumption",
    confidence: 0.70,
    correlated_with: [
      { param: "churn_rate", coefficient: -0.3 }
    ]
  }
```

### ❌ Invalid Syntax

```pel
// Old correlation syntax - DO NOT USE
param growth_rate: Rate per Month 
  ~ Normal(μ=0.15/1mo, σ=0.05/1mo) 
  with correlation(churn_rate: -0.3) {    // ❌ Invalid
    source: "forecast",
    method: "assumption",
    confidence: 0.70
  }
```

## Documentation Links

### ✅ Valid Links

```markdown
- [Type System](../../spec/pel_type_system.md)
- [Language Spec](../../spec/pel_language_spec.md)
- [Examples](../../examples/)
- [Standard Library](../../stdlib/)
```

### ❌ Broken Links (Do Not Use)

```markdown
- [Type System](/docs/model/types.md)           // ❌ Does not exist
- [Runtime](/docs/runtime/execution.md)         // ❌ Does not exist
- [Patterns](/docs/patterns/patterns.md)        // ❌ Does not exist
```

## Testing Your Tutorial

### 1. Validate Code Blocks

Run the tutorial validator to check all PEL code:

```bash
python scripts/validate_tutorial_code.py --tutorial YOUR_TUTORIAL.md --verbose
```

This checks for:
- Invalid types (Probability, Bool, etc.)
- Invalid syntax patterns
- Missing provenance metadata

### 2. Check Links

Verify all internal links point to existing files:

```bash
# Check for broken links
grep -o '\[.*\](.*\.md)' docs/tutorials/YOUR_TUTORIAL.md | \
  grep -o '(.*\.md)' | \
  tr -d '()' | \
  while read link; do
    if [[ "$link" == http* ]]; then
      continue
    fi
    full_path="docs/tutorials/$link"
    if [ ! -f "$full_path" ]; then
      echo "❌ Broken link: $link"
    fi
  done
```

### 3. Run Full CI Validation

The tutorial-qa.yml workflow will automatically run on PRs:

```bash
# Simulate CI checks locally
python scripts/validate_tutorial_code.py
```

## Code Example Guidelines

### Complete Examples

Provide **complete, runnable examples**:

```pel
model SaaSMetrics {
  // Parameters with provenance
  param initial_users: Fraction = 1000.0 {
    source: "analytics",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_growth: Rate per Month = 0.15 / 1mo {
    source: "historical_average",
    method: "fitted",
    confidence: 0.80
  }
  
  // Complete calculation
  var users: TimeSeries<Fraction>
  users[0] = initial_users
  users[t+1] = users[t] * (1.0 + monthly_growth * 1mo)
}
```

### Provenance Metadata

**Always include provenance** in examples with parameters:

```pel
param conversion_rate: Fraction = 0.12 {
  source: "ab_test_results",           // Where did this come from?
  method: "observed",                  // How was it determined?
  confidence: 0.85,                    // How confident are we?
  notes: "A/B test from Q4 2025"      // Additional context
}
```

### Realistic Values

Use **realistic business values**:

```pel
// ✅ Good - realistic SaaS metrics
param mrr: Currency<USD> = $50_000
param churn_rate: Fraction = 0.05    // 5% monthly churn

// ❌ Avoid - unrealistic values
param mrr: Currency<USD> = $1
param churn_rate: Fraction = 0.99    // 99% churn is unrealistic
```

## Security Best Practices

If demonstrating production deployment or API integration:

### ✅ Secure Code Examples

```python
# Allowlist permitted models
ALLOWED_MODELS = {"model1", "model2"}

def run_model(model_name):
    # Validate against allowlist
    if model_name not in ALLOWED_MODELS:
        raise ValueError("Model not allowed")
    
    # Validate path stays within directory
    model_path = os.path.join(MODEL_DIR, f"{model_name}.ir.json")
    model_dir_abs = os.path.abspath(MODEL_DIR)
    model_path_abs = os.path.abspath(model_path)
    
    if os.path.commonpath([model_dir_abs, model_path_abs]) != model_dir_abs:
        raise ValueError("Invalid model path")
    
    # Now safe to use
    return subprocess.run(["pel", "run", model_path_abs])
```

### ❌ Insecure Code Examples (Do Not Show)

```python
# ❌ Vulnerable to path traversal
def run_model(model_name):
    model_path = f"{MODEL_DIR}/{model_name}.ir.json"  # No validation!
    return subprocess.run(["pel", "run", model_path])
```

## File Naming Conventions

- Use numbered prefixes: `02_economic_types.md`
- Use snake_case: `migration_spreadsheets.md`
- Be descriptive: `10_production_deployment.md` not `10_prod.md`

## Time Estimates

Provide realistic time estimates:
- Include time to read, understand, and run examples
- Test with actual users if possible
- Round to nearest 5 minutes
- Include in both tutorial header and README metadata

## Accessibility

### Code Formatting

```markdown
// ✅ Good - syntax highlighting
\`\`\`pel
model Example { }
\`\`\`

// ❌ Avoid - no syntax highlighting
\`\`\`
model Example { }
\`\`\`
```

### Progressive Disclosure

Use `<details>` for optional content:

```markdown
<details>
<summary>Advanced: Why use this approach?</summary>

Detailed explanation that doesn't clutter the main flow.

</details>
```

## Submission Checklist

Before submitting a new tutorial:

- [ ] Code examples use valid PEL types
- [ ] All code blocks are marked with ````pel`
- [ ] Provenance metadata included in examples
- [ ] All links point to existing files
- [ ] Time estimate is realistic
- [ ] Prerequisites are listed
- [ ] Learning outcomes are clear
- [ ] Quiz questions test key concepts
- [ ] Key takeaways summarize main points
- [ ] Ran `python scripts/validate_tutorial_code.py`
- [ ] No security antipatterns in examples
- [ ] Consistent formatting with other tutorials

## Getting Help

- **Questions?** [Start a discussion](https://github.com/Coding-Krakken/pel-lang/discussions)
- **Found a bug?** [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues)
- **Need review?** Tag `@Coding-Krakken` in your PR

## Examples of Excellent Tutorials

See these tutorials as examples of our quality standards:
- Tutorial 02: Economic Types - Great type system coverage
- Tutorial 03: Uncertainty & Distributions - Excellent code examples
- Tutorial 06: Time-Series Modeling - Strong pedagogical flow

---

Thank you for contributing to PEL education! 🎓
