"""
LLM Prompt Testing Framework
Main entry point for running tests
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

from framework.reporter import Reporter
from framework.runner import TestRunner


def main():
    parser = argparse.ArgumentParser(description='Test LLM prompts with comprehensive evaluation')
    parser.add_argument('prompt', help='Path to prompt file or direct prompt text')
    parser.add_argument('--config', help='Path to config file for this prompt', default=None)
    parser.add_argument('--test-cases', help='Path to test cases file', default=None)
    parser.add_argument('--output', help='Output directory for results', default='.testing/results')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--template', help='Template type (code, transform, qa, creative)', default='generic')

    args = parser.parse_args()

    # Load environment variables
    load_dotenv(Path(__file__).parent / '.env')

    # Determine if input is file or text
    prompt_path = Path(args.prompt)
    if prompt_path.exists():
        print(f"📄 Testing prompt from file: {prompt_path}")
        with open(prompt_path, encoding='utf-8') as f:
            prompt_text = f.read()
        prompt_name = prompt_path.stem

        # Auto-discover prompt-specific config/test-cases if not provided
        testing_root = Path(__file__).parent
        default_config = testing_root / 'config' / 'prompts' / f'{prompt_name}.yaml'
        default_tests = testing_root / 'config' / 'testcases' / f'{prompt_name}.yaml'

        if args.config is None and default_config.exists():
            args.config = str(default_config)
            if args.verbose:
                print(f"🔧 Using prompt-specific config: {default_config}")

        if args.test_cases is None and default_tests.exists():
            args.test_cases = str(default_tests)
            if args.verbose:
                print(f"🧪 Using prompt-specific test cases: {default_tests}")
    else:
        print("📝 Testing prompt from text input")
        prompt_text = args.prompt
        prompt_name = "inline_prompt"

    try:
        # Initialize runner
        runner = TestRunner(
            prompt_text=prompt_text,
            prompt_name=prompt_name,
            config_path=args.config,
            test_cases_path=args.test_cases,
            template=args.template,
            verbose=args.verbose
        )

        # Run tests
        print("\n🚀 Starting prompt evaluation...\n")
        results = runner.run()
    except RuntimeError as e:
        print(f"\n❌ {e}\n")
        print("Fix: copy .testing/.env.example to .testing/.env and set the required API key(s).")
        sys.exit(2)

    # Generate report
    reporter = Reporter(results, args.output)
    report_path = reporter.generate_report()

    print("\n✅ Testing complete!")
    print(f"📊 Report saved to: {report_path}")
    print(f"\n{'='*60}")
    print(reporter.get_summary())
    print(f"{'='*60}\n")

    # Exit with appropriate code
    if results['overall_score'] >= 70:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
