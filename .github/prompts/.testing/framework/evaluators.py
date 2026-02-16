"""
Evaluator classes for different types of prompt testing
"""

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import jsonschema
from anthropic import Anthropic
from openai import OpenAI


class Evaluator(ABC):
    """Base evaluator class"""

    @abstractmethod
    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate the output
        Returns: {
            'score': float (0-100),
            'passed': bool,
            'feedback': str,
            'details': dict
        }
        """
        pass


class RegexEvaluator(Evaluator):
    """Validates output against regex patterns"""

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        patterns = criteria.get('patterns', [])
        must_match = criteria.get('must_match', [])
        must_not_match = criteria.get('must_not_match', [])

        score = 100
        feedback_parts = []
        details = {'matches': [], 'failures': []}

        # Check must_match patterns
        for pattern in must_match:
            if re.search(pattern, output, re.IGNORECASE | re.DOTALL):
                details['matches'].append(f"✓ Matched: {pattern}")
            else:
                score -= 100 / (len(must_match) + len(must_not_match))
                details['failures'].append(f"✗ Missing: {pattern}")

        # Check must_not_match patterns
        for pattern in must_not_match:
            if not re.search(pattern, output, re.IGNORECASE | re.DOTALL):
                details['matches'].append(f"✓ Correctly absent: {pattern}")
            else:
                score -= 100 / (len(must_match) + len(must_not_match))
                details['failures'].append(f"✗ Should not match: {pattern}")

        score = max(0, score)
        passed = score >= criteria.get('threshold', 80)
        feedback = '\n'.join(details['matches'] + details['failures'])

        return {
            'score': score,
            'passed': passed,
            'feedback': feedback,
            'details': details
        }


class JsonSchemaEvaluator(Evaluator):
    """Validates JSON output against a schema"""

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        schema = criteria.get('schema')
        extract_json = criteria.get('extract_json', True)

        details = {}

        try:
            # Try to extract JSON from markdown code blocks
            if extract_json:
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                else:
                    # Try to find raw JSON
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    json_text = json_match.group(0) if json_match else output
            else:
                json_text = output

            parsed = json.loads(json_text)
            details['parsed_json'] = parsed

            # Validate against schema
            if schema:
                jsonschema.validate(instance=parsed, schema=schema)
                details['schema_valid'] = True

            return {
                'score': 100,
                'passed': True,
                'feedback': '✓ Valid JSON structure matching schema',
                'details': details
            }

        except json.JSONDecodeError as e:
            return {
                'score': 0,
                'passed': False,
                'feedback': f'✗ Invalid JSON: {str(e)}',
                'details': {'error': str(e)}
            }
        except jsonschema.ValidationError as e:
            return {
                'score': 50,
                'passed': False,
                'feedback': f'✗ JSON schema validation failed: {e.message}',
                'details': {'error': e.message, 'parsed_json': parsed}
            }


class ChecklistEvaluator(Evaluator):
    """Checks for presence of required elements"""

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        required_elements = criteria.get('required_elements', [])
        optional_elements = criteria.get('optional_elements', [])

        found = []
        missing = []

        for element in required_elements:
            if element.lower() in output.lower():
                found.append(f"✓ {element}")
            else:
                missing.append(f"✗ {element}")

        optional_found = []
        for element in optional_elements:
            if element.lower() in output.lower():
                optional_found.append(f"+ {element}")

        # Score based on required elements
        score = (len(found) / len(required_elements) * 100) if required_elements else 100

        # Bonus for optional elements (up to 10 points)
        if optional_elements:
            bonus = (len(optional_found) / len(optional_elements)) * 10
            score = min(100, score + bonus)

        passed = score >= criteria.get('threshold', 80)
        feedback = '\n'.join(found + missing + optional_found)

        return {
            'score': score,
            'passed': passed,
            'feedback': feedback,
            'details': {
                'found': found,
                'missing': missing,
                'optional_found': optional_found
            }
        }


class LengthEvaluator(Evaluator):
    """Validates output length constraints"""

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        min_length = criteria.get('min_length', 0)
        max_length = criteria.get('max_length', float('inf'))
        count_by = criteria.get('count_by', 'characters')  # 'characters' or 'words'

        if count_by == 'words':
            length = len(output.split())
            unit = 'words'
        else:
            length = len(output)
            unit = 'characters'

        details = {
            'length': length,
            'min_required': min_length,
            'max_allowed': max_length,
            'unit': unit
        }

        if length < min_length:
            score = (length / min_length) * 100
            passed = False
            feedback = f'✗ Too short: {length} {unit} (minimum: {min_length})'
        elif length > max_length:
            score = max(0, 100 - ((length - max_length) / max_length * 50))
            passed = False
            feedback = f'✗ Too long: {length} {unit} (maximum: {max_length})'
        else:
            score = 100
            passed = True
            feedback = f'✓ Length acceptable: {length} {unit}'

        return {
            'score': score,
            'passed': passed,
            'feedback': feedback,
            'details': details
        }


class LLMJudgeEvaluator(Evaluator):
    """Uses an LLM to evaluate output quality"""

    def __init__(self):
        self.provider = os.getenv('JUDGE_PROVIDER', 'openai')
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise RuntimeError(
                    "Missing OPENAI_API_KEY. Set it in .testing/.env (copy from .testing/.env.example)."
                )
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        else:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise RuntimeError(
                    "Missing ANTHROPIC_API_KEY. Set it in .testing/.env (copy from .testing/.env.example)."
                )
            self.client = Anthropic(api_key=api_key)
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        rubric = criteria.get('rubric', 'Evaluate the quality of this output.')
        aspects = criteria.get('aspects', ['accuracy', 'completeness', 'clarity'])

        judge_prompt = f"""You are an expert evaluator. Assess the following output based on this rubric:

RUBRIC: {rubric}

TEST INPUT: {test_case.get('input', 'N/A')}

OUTPUT TO EVALUATE:
{output}

Evaluate the output on these aspects: {', '.join(aspects)}

Provide your evaluation in this JSON format:
{{
    "overall_score": <0-100>,
    "aspect_scores": {{
        {', '.join([f'"{aspect}": <0-100>' for aspect in aspects])}
    }},
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "feedback": "detailed feedback text"
}}

Be critical but fair. Only give high scores for truly excellent outputs."""

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise evaluator. Always respond with valid JSON."},
                        {"role": "user", "content": judge_prompt}
                    ],
                    temperature=0.3
                )
                result_text = response.choices[0].message.content
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": judge_prompt}
                    ],
                    temperature=0.3
                )
                result_text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = json.loads(result_text)

            score = result.get('overall_score', 0)
            passed = score >= criteria.get('threshold', 70)

            feedback_parts = [
                f"Overall Score: {score}/100",
                "\nStrengths:",
                *[f"  ✓ {s}" for s in result.get('strengths', [])],
                "\nWeaknesses:",
                *[f"  ✗ {w}" for w in result.get('weaknesses', [])],
                f"\n{result.get('feedback', '')}"
            ]

            return {
                'score': score,
                'passed': passed,
                'feedback': '\n'.join(feedback_parts),
                'details': result
            }

        except Exception as e:
            return {
                'score': 0,
                'passed': False,
                'feedback': f'✗ LLM Judge evaluation failed: {str(e)}',
                'details': {'error': str(e)}
            }


class SimilarityEvaluator(Evaluator):
    """Compares output to expected output"""

    def evaluate(self, output: str, criteria: dict[str, Any], test_case: dict[str, Any]) -> dict[str, Any]:
        expected = test_case.get('expected_output', '')

        if not expected:
            return {
                'score': 100,
                'passed': True,
                'feedback': 'No expected output provided for comparison',
                'details': {}
            }

        # Simple word-based similarity
        output_words = set(output.lower().split())
        expected_words = set(expected.lower().split())

        if not expected_words:
            similarity = 100
        else:
            intersection = output_words & expected_words
            union = output_words | expected_words
            similarity = (len(intersection) / len(union)) * 100 if union else 0

        details = {
            'similarity_score': similarity,
            'output_words': len(output_words),
            'expected_words': len(expected_words),
            'common_words': len(output_words & expected_words)
        }

        passed = similarity >= criteria.get('threshold', 60)

        if similarity >= 80:
            feedback = f'✓ High similarity ({similarity:.1f}%) to expected output'
        elif similarity >= 60:
            feedback = f'~ Moderate similarity ({similarity:.1f}%) to expected output'
        else:
            feedback = f'✗ Low similarity ({similarity:.1f}%) to expected output'

        return {
            'score': similarity,
            'passed': passed,
            'feedback': feedback,
            'details': details
        }


# Evaluator registry
EVALUATORS = {
    'regex': RegexEvaluator,
    'json_schema': JsonSchemaEvaluator,
    'checklist': ChecklistEvaluator,
    'length': LengthEvaluator,
    'llm_judge': LLMJudgeEvaluator,
    'similarity': SimilarityEvaluator,
}


def get_evaluator(evaluator_type: str) -> Evaluator:
    """Get evaluator instance by type"""
    evaluator_class = EVALUATORS.get(evaluator_type)
    if not evaluator_class:
        raise ValueError(f"Unknown evaluator type: {evaluator_type}")
    return evaluator_class()
