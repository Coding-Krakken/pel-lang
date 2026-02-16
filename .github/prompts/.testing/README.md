# LLM Prompt Testing Framework

A comprehensive, production-ready testing framework for evaluating and scoring LLM prompts with automated evaluation, detailed analytics, and actionable feedback.

## 🚀 Quick Start

Note (Windows): if you have multiple Python versions installed, `npm` scripts are pinned to `py -3.12` to avoid running the framework under a different interpreter without dependencies.

### Installation

1. Install Python dependencies:
```bash
npm run install-deps
# or (Windows)
py -m pip install -r .testing/requirements.txt
# or (any OS)
python -m pip install -r .testing/requirements.txt
```

Optional one-shot setup (recommended on Windows):
```bash
npm run setup
```

2. Set up your API keys:
```bash
cp .testing/.env.example .testing/.env
# Edit .testing/.env with your API keys
```

### Basic Usage

Test any prompt file:
```bash
npm test path/to/your/prompt.md
```

Test with inline prompt text:
```bash
npm test "You are a helpful assistant. Summarize the following text:"
```

Test with custom configuration:
```bash
npm test prompt.md --config custom-config.yaml
```

Test with specific template:
```bash
npm test prompt.md --template code
```

## 📋 Features

### ✅ Multiple Evaluator Types

1. **Regex Evaluator** - Pattern matching validation
2. **JSON Schema Evaluator** - Structured data validation
3. **Checklist Evaluator** - Required elements verification
4. **Length Evaluator** - Output length constraints
5. **LLM Judge Evaluator** - AI-powered quality assessment
6. **Similarity Evaluator** - Compare to expected outputs

### 📊 Comprehensive Scoring

- Category-based evaluation with configurable weights
- Overall score calculation with pass/fail thresholds
- Detailed feedback for each test case
- Pass rate tracking across multiple tests

### 📈 Report Generation

- **Markdown Reports** - Human-readable with tables and formatting
- **JSON Reports** - Full data export for programmatic analysis
- **Text Reports** - Terminal-friendly colored output
- **Summary Dashboard** - Quick overview of results

### 🎯 Template System

Pre-configured templates for common use cases:
- `generic` - General purpose prompts
- `code` - Code generation prompts
- `transform` - Data transformation prompts
- `qa` - Question answering / RAG prompts
- `creative` - Creative writing prompts

## 📚 Configuration

### Using Templates

Templates provide pre-configured evaluation criteria for specific prompt types:

```bash
npm test prompt.md --template code
```

Available templates:
- **generic**: Balanced evaluation for general prompts
- **code**: Syntax, structure, and code quality
- **transform**: Data accuracy and format compliance
- **qa**: Accuracy, completeness, and clarity
- **creative**: Creativity, coherence, and writing quality

### Custom Configuration

Create a custom YAML configuration file to override template settings:

```yaml
# my-config.yaml
version: '1.0'
pass_threshold: 75

evaluation:
  format:
    weight: 30
    evaluator: 'regex'
    criteria:
      must_match:
        - 'function'
        - 'return'
      must_not_match:
        - 'TODO'
      threshold: 90
  
  quality:
    weight: 70
    evaluator: 'llm_judge'
    criteria:
      rubric: 'Evaluate code quality and best practices'
      aspects: ['readability', 'efficiency', 'maintainability']
      threshold: 80

test_cases:
  - id: 'test1'
    name: 'Basic Test'
    input: 'Create a function to reverse a string'
    expected_output: 'function reverse(str) { return str.split("").reverse().join(""); }'
```

### Test Cases File

Define custom test cases in a separate file:

```yaml
# test-cases.yaml
test_cases:
  - id: 'typical_case'
    name: 'Typical Input'
    description: 'Tests standard use case'
    input: 'Standard input here'
    expected_output: 'Expected output here'
  
  - id: 'edge_case'
    name: 'Edge Case'
    description: 'Tests edge conditions'
    input: ''
  
  - id: 'complex_case'
    name: 'Complex Scenario'
    description: 'Tests complex multi-step scenario'
    input: 'Complex input with multiple requirements'
```

Use with:
```bash
npm test prompt.md --test-cases test-cases.yaml
```

## 🔧 Evaluation Categories

### Format Validation (Regex)

```yaml
format:
  weight: 20
  evaluator: 'regex'
  criteria:
    must_match:
      - 'pattern1'
      - 'pattern2'
    must_not_match:
      - 'anti-pattern'
    threshold: 80
```

### JSON Schema Validation

```yaml
json_validation:
  weight: 30
  evaluator: 'json_schema'
  criteria:
    extract_json: true
    schema:
      type: 'object'
      required: ['id', 'name']
      properties:
        id:
          type: 'integer'
        name:
          type: 'string'
    threshold: 100
```

### Checklist Validation

```yaml
completeness:
  weight: 25
  evaluator: 'checklist'
  criteria:
    required_elements:
      - 'introduction'
      - 'conclusion'
    optional_elements:
      - 'examples'
      - 'references'
    threshold: 80
```

### Length Validation

```yaml
length_check:
  weight: 15
  evaluator: 'length'
  criteria:
    min_length: 50
    max_length: 500
    count_by: 'words'  # or 'characters'
    threshold: 90
```

### LLM Judge

```yaml
quality:
  weight: 50
  evaluator: 'llm_judge'
  criteria:
    rubric: 'Detailed criteria for evaluation'
    aspects:
      - 'accuracy'
      - 'completeness'
      - 'clarity'
    threshold: 70
```

### Similarity Comparison

```yaml
similarity:
  weight: 30
  evaluator: 'similarity'
  criteria:
    threshold: 70
```

## 📊 Understanding Results

### Score Interpretation

- **90-100**: 🟢 Excellent - Production ready
- **80-89**: 🟢 Good - Minor improvements possible
- **70-79**: 🟡 Acceptable - Passes but could be refined
- **60-69**: 🟠 Needs Improvement - Review recommended
- **0-59**: 🔴 Poor - Significant issues, refactor needed

### Report Files

After testing, find reports in `.testing/results/`:
- `[prompt_name]_[timestamp].md` - Main human-readable report
- `[prompt_name]_[timestamp].json` - Full data export
- `[prompt_name]_[timestamp].txt` - Terminal-friendly format

### Terminal Output

The framework provides immediate feedback:
```
🚀 Starting prompt evaluation...

[1/3] Running test: Basic Test
  ✓ Execution successful (1.23s)
  📊 Score: 85.5/100 ✓ PASS

✅ Testing complete!
📊 Report saved to: .testing/results/my_prompt_20260213_143022.md

================================================================
PROMPT: my_prompt
OVERALL SCORE: 85.5/100
GRADE: GOOD
PASS RATE: 100.0% (3/3 tests)
================================================================
```

## 🎯 Advanced Usage

### Python API

Use the framework programmatically:

```python
from .testing.framework import TestRunner, Reporter

runner = TestRunner(
    prompt_text="Your prompt here",
    prompt_name="my_prompt",
    template="code",
    verbose=True
)

results = runner.run()
reporter = Reporter(results, ".testing/results")
report_path = reporter.generate_report()

print(f"Score: {results['overall_score']}")
```

### Custom Evaluators

Extend the framework with custom evaluators:

```python
from .testing.framework.evaluators import Evaluator, EVALUATORS

class CustomEvaluator(Evaluator):
    def evaluate(self, output, criteria, test_case):
        # Your custom logic here
        return {
            'score': 85.0,
            'passed': True,
            'feedback': 'Evaluation feedback',
            'details': {}
        }

# Register your evaluator
EVALUATORS['custom'] = CustomEvaluator
```

### Batch Testing

Test multiple prompts:

```bash
# Test all prompts in a directory
for file in Development/prompts/*.md; do
    npm test "$file" --output ".testing/results/$(basename $file .md)"
done
```

## 🔍 Best Practices

### 1. Test Comprehensively
- Include typical cases, edge cases, and adversarial examples
- Test with empty inputs, malformed data, and unexpected formats
- Cover different input lengths and complexity levels

### 2. Set Appropriate Thresholds
- **Production prompts**: Set pass threshold to 80+
- **Experimental prompts**: 70 is acceptable for iteration
- Adjust category weights based on what matters most

### 3. Use Multiple Evaluators
- Combine deterministic checks (regex, schema) with LLM judge
- Use checklist for required elements
- Add length constraints to prevent overly verbose outputs

### 4. Iterate Based on Feedback
- Review detailed feedback for failed tests
- Focus on categories with lowest scores
- Use recommendations section in reports

### 5. Version Control
- Commit test configurations alongside prompts
- Track score trends over prompt versions
- Keep test cases in version control

## 🛠️ Troubleshooting

### API Key Issues
```bash
# Check if .env file exists
cat .testing/.env

# Verify API keys are set
echo $OPENAI_API_KEY
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r .testing/requirements.txt --force-reinstall
```

### Test Execution Failures
- Check API rate limits
- Verify prompt syntax
- Review test case inputs for validity

### Low Scores
- Review detailed feedback in reports
- Check if prompt is specific enough
- Consider adding examples or constraints to prompt
- Adjust evaluation criteria if too strict

## 📞 Environment Variables

Required in `.testing/.env`:

```bash
# OpenAI (if using)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic (if using)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Default provider for LLM Judge
JUDGE_PROVIDER=openai  # or 'anthropic'
```

## 🎓 Examples

See `.testing/examples/` directory for:
- Example custom configurations
- Sample test case files
- Template usage examples
- Advanced configuration patterns

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new evaluator types
- Create new templates
- Improve documentation
- Report issues or suggest features
