"""
Test runner that orchestrates prompt testing
"""

import os
import time
from pathlib import Path
from typing import Any

import yaml
from anthropic import Anthropic
from openai import OpenAI

from .config_loader import ConfigLoader
from .evaluators import get_evaluator


class TestRunner:
    """Orchestrates prompt testing and evaluation"""

    def __init__(
        self,
        prompt_text: str,
        prompt_name: str,
        config_path: str = None,
        test_cases_path: str = None,
        template: str = 'generic',
        verbose: bool = False
    ):
        self.prompt_text = prompt_text
        self.prompt_name = prompt_name
        self.verbose = verbose
        self.template = template

        # Load configuration
        self.config_loader = ConfigLoader(
            config_path=config_path,
            template=template
        )
        self.config = self.config_loader.load()

        # Load test cases
        self.test_cases = self._load_test_cases(test_cases_path)

        # Initialize LLM client
        self.llm_provider = os.getenv('JUDGE_PROVIDER', 'openai')
        if self.llm_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise RuntimeError(
                    "Missing OPENAI_API_KEY. Set it in .testing/.env (copy from .testing/.env.example)."
                )
            self.llm_client = OpenAI(api_key=api_key)
            self.llm_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        else:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise RuntimeError(
                    "Missing ANTHROPIC_API_KEY. Set it in .testing/.env (copy from .testing/.env.example)."
                )
            self.llm_client = Anthropic(api_key=api_key)
            self.llm_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

    def _load_test_cases(self, test_cases_path: str = None) -> list[dict[str, Any]]:
        """Load test cases from file or use defaults"""
        if test_cases_path and Path(test_cases_path).exists():
            with open(test_cases_path, encoding='utf-8') as f:
                return yaml.safe_load(f).get('test_cases', [])

        # Use test cases from config
        if 'test_cases' in self.config:
            return self.config['test_cases']

        # Generate default test cases
        return [
            {
                'id': 'default_case',
                'name': 'Default Test Case',
                'input': 'Test input for prompt evaluation',
                'description': 'Basic test case'
            }
        ]

    def _execute_prompt(self, test_input: str) -> dict[str, Any]:
        """Execute the prompt with test input against LLM"""
        # Construct full prompt
        full_prompt = f"{self.prompt_text}\n\nInput: {test_input}"

        start_time = time.time()

        try:
            if self.llm_provider == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7
                )
                output = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
            else:
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7
                )
                output = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            execution_time = time.time() - start_time

            return {
                'success': True,
                'output': output,
                'execution_time': execution_time,
                'tokens_used': tokens_used,
                'error': None
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'output': '',
                'execution_time': execution_time,
                'tokens_used': 0,
                'error': str(e)
            }

    def _evaluate_output(self, output: str, test_case: dict[str, Any]) -> dict[str, Any]:
        """Evaluate output against all configured criteria"""
        category_results = {}

        for category_name, category_config in self.config['evaluation'].items():
            if self.verbose:
                print(f"  → Evaluating: {category_name}")

            evaluator_type = category_config['evaluator']
            evaluator = get_evaluator(evaluator_type)

            criteria = category_config.get('criteria', {})
            result = evaluator.evaluate(output, criteria, test_case)

            category_results[category_name] = {
                **result,
                'weight': category_config.get('weight', 1.0),
                'evaluator': evaluator_type
            }

        return category_results

    def _calculate_overall_score(self, category_results: dict[str, Any]) -> float:
        """Calculate weighted overall score"""
        total_weight = sum(r['weight'] for r in category_results.values())

        if total_weight == 0:
            return 0

        weighted_score = sum(
            r['score'] * r['weight']
            for r in category_results.values()
        )

        return weighted_score / total_weight

    def run(self) -> dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print(f"Testing prompt: {self.prompt_name}")
        print(f"Template: {self.template}")
        print(f"Test cases: {len(self.test_cases)}")
        print(f"Evaluation categories: {len(self.config['evaluation'])}\n")

        test_results = []

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] Running test: {test_case.get('name', test_case['id'])}")

            # Execute prompt
            execution_result = self._execute_prompt(test_case['input'])

            if not execution_result['success']:
                print(f"  ✗ Execution failed: {execution_result['error']}")
                test_results.append({
                    'test_case': test_case,
                    'execution': execution_result,
                    'evaluation': {},
                    'overall_score': 0,
                    'passed': False
                })
                continue

            if self.verbose:
                print(f"  ✓ Execution successful ({execution_result['execution_time']:.2f}s)")

            # Evaluate output
            category_results = self._evaluate_output(
                execution_result['output'],
                test_case
            )

            # Calculate overall score
            overall_score = self._calculate_overall_score(category_results)
            passed = overall_score >= self.config.get('pass_threshold', 70)

            print(f"  📊 Score: {overall_score:.1f}/100 {'✓ PASS' if passed else '✗ FAIL'}\n")

            test_results.append({
                'test_case': test_case,
                'execution': execution_result,
                'evaluation': category_results,
                'overall_score': overall_score,
                'passed': passed
            })

        # Aggregate results
        all_scores = [r['overall_score'] for r in test_results]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        pass_rate = sum(1 for r in test_results if r['passed']) / len(test_results) * 100 if test_results else 0

        return {
            'prompt_name': self.prompt_name,
            'prompt_text': self.prompt_text,
            'template': self.template,
            'config': self.config,
            'test_results': test_results,
            'overall_score': avg_score,
            'pass_rate': pass_rate,
            'total_tests': len(test_results),
            'passed_tests': sum(1 for r in test_results if r['passed']),
            'failed_tests': sum(1 for r in test_results if not r['passed']),
        }
