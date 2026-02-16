# Quick Start Guide

## 1. Installation (2 minutes)

```bash
# Navigate to your prompts directory
cd c:\Users\david\Desktop\prompts

# One-shot setup (recommended on Windows)
npm run setup

# Setup environment variables
cp .testing/.env.example .testing/.env
# Edit .testing/.env and add your API keys
```

## 2. First Test (1 minute)

Test one of your existing prompts:

```bash
npm test Development/model-first-prompts/convert.prompt.md
```

Or test with a specific template:

```bash
npm test Development/model-first-prompts/convert.prompt.md --template transform
```

## 3. View Results

After testing completes, check:
- Terminal output for immediate summary
- `.testing/results/` folder for detailed reports
- Open the `.md` file for the most readable report

## 4. Customize (Optional)

Create a custom config for your prompt:

```yaml
# my-prompt-config.yaml
version: '1.0'
pass_threshold: 75

evaluation:
  accuracy:
    weight: 60
    evaluator: 'llm_judge'
    criteria:
      rubric: 'Does it correctly transform the model?'
      aspects: ['accuracy', 'completeness']
      threshold: 80
  
  format:
    weight: 40
    evaluator: 'json_schema'
    criteria:
      extract_json: true
      schema:
        type: 'object'
        required: ['name', 'properties']

test_cases:
  - id: 'test1'
    name: 'Simple Model'
    input: 'Convert User model with name and email fields'
```

Test with your config:
```bash
npm test your-prompt.md --config my-prompt-config.yaml
```

## 5. Common Commands

```bash
# Test with verbose output
npm test prompt.md --verbose

# Test with custom test cases
npm test prompt.md --test-cases my-tests.yaml

# Test multiple prompts
npm test prompt1.md
npm test prompt2.md
npm test prompt3.md

# View example configurations
ls .testing/examples/
```

## 6. Understanding Scores

- **90-100**: 🟢 Excellent - Production ready
- **80-89**: 🟢 Good - Minor improvements possible
- **70-79**: 🟡 Acceptable - Passes but refinement recommended
- **60-69**: 🟠 Needs Work - Review required
- **0-59**: 🔴 Poor - Significant improvements needed

## Next Steps

1. Read the full [README](.testing/README.md)
2. Check [examples](.testing/examples/) for advanced usage
3. Create custom configurations for your specific prompts
4. Set up automated testing in your workflow

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r .testing/requirements.txt --force-reinstall
```

**API errors:**
- Verify API keys in `.testing/.env`
- Check API rate limits
- Ensure correct model names

**Low scores:**
- Review detailed feedback in reports
- Adjust evaluation criteria in config
- Refine your prompt based on feedback

## Support

For issues or questions:
1. Check the [README](.testing/README.md)
2. Review [examples](.testing/examples/)
3. Check configuration templates in `.testing/config/templates/`
