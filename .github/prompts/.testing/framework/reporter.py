"""
Report generator for test results
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)


class Reporter:
    """Generates reports from test results"""

    def __init__(self, results: dict[str, Any], output_dir: str):
        self.results = results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.prompt_name = results['prompt_name']

    def generate_report(self) -> str:
        """Generate all report formats and return main report path"""
        # Generate JSON report (full data)
        json_path = self._generate_json_report()

        # Generate human-readable report
        text_path = self._generate_text_report()

        # Generate markdown report
        md_path = self._generate_markdown_report()

        return md_path

    def _generate_json_report(self) -> str:
        """Generate JSON report with all data"""
        filename = f"{self.prompt_name}_{self.timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return filepath

    def _generate_text_report(self) -> str:
        """Generate colored terminal-friendly report"""
        filename = f"{self.prompt_name}_{self.timestamp}.txt"
        filepath = self.output_dir / filename

        lines = []
        lines.append("=" * 80)
        lines.append(f"PROMPT TEST REPORT: {self.prompt_name}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Overall Score: {self.results['overall_score']:.1f}/100")
        lines.append(f"Pass Rate: {self.results['pass_rate']:.1f}%")
        lines.append(f"Tests: {self.results['passed_tests']}/{self.results['total_tests']} passed")
        lines.append("")

        # Test Results
        for i, test_result in enumerate(self.results['test_results'], 1):
            lines.append(f"TEST {i}: {test_result['test_case'].get('name', test_result['test_case']['id'])}")
            lines.append("-" * 80)
            lines.append(f"Status: {'PASS' if test_result['passed'] else 'FAIL'}")
            lines.append(f"Score: {test_result['overall_score']:.1f}/100")
            lines.append(f"Execution Time: {test_result['execution']['execution_time']:.2f}s")
            lines.append(f"Tokens Used: {test_result['execution']['tokens_used']}")
            lines.append("")

            # Category breakdown
            lines.append("Category Scores:")
            for cat_name, cat_result in test_result['evaluation'].items():
                status = "✓" if cat_result['passed'] else "✗"
                lines.append(f"  {status} {cat_name}: {cat_result['score']:.1f}/100 (weight: {cat_result['weight']})")
            lines.append("")

            # Detailed feedback
            lines.append("Detailed Feedback:")
            for cat_name, cat_result in test_result['evaluation'].items():
                lines.append(f"\n  [{cat_name}]")
                for line in cat_result['feedback'].split('\n'):
                    if line.strip():
                        lines.append(f"    {line}")
            lines.append("")
            lines.append("")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return filepath

    def _generate_markdown_report(self) -> str:
        """Generate markdown report"""
        filename = f"{self.prompt_name}_{self.timestamp}.md"
        filepath = self.output_dir / filename

        lines = []
        lines.append(f"# Prompt Test Report: {self.prompt_name}")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Template:** {self.results['template']}")
        lines.append("\n---\n")

        # Summary
        lines.append("## 📊 Summary\n")

        summary_table = [
            ["Overall Score", f"{self.results['overall_score']:.1f}/100"],
            ["Pass Rate", f"{self.results['pass_rate']:.1f}%"],
            ["Tests Passed", f"{self.results['passed_tests']}/{self.results['total_tests']}"],
            ["Tests Failed", str(self.results['failed_tests'])],
        ]

        lines.append(tabulate(summary_table, tablefmt='pipe'))
        lines.append("")

        # Grade
        score = self.results['overall_score']
        if score >= 90:
            grade = "🟢 Excellent"
        elif score >= 80:
            grade = "🟢 Good"
        elif score >= 70:
            grade = "🟡 Acceptable"
        elif score >= 60:
            grade = "🟠 Needs Improvement"
        else:
            grade = "🔴 Poor"

        lines.append(f"\n**Grade:** {grade}\n")

        # Detailed Results
        lines.append("---\n")
        lines.append("## 📋 Detailed Test Results\n")

        for i, test_result in enumerate(self.results['test_results'], 1):
            test_case = test_result['test_case']
            status_emoji = "✅" if test_result['passed'] else "❌"

            lines.append(f"### {status_emoji} Test {i}: {test_case.get('name', test_case['id'])}\n")

            # Test info
            lines.append(f"**Description:** {test_case.get('description', 'N/A')}")
            lines.append(f"**Score:** {test_result['overall_score']:.1f}/100")
            lines.append(f"**Execution Time:** {test_result['execution']['execution_time']:.2f}s")
            lines.append(f"**Tokens Used:** {test_result['execution']['tokens_used']}\n")

            # Test input
            lines.append("**Input:**")
            lines.append(f"```\n{test_case['input']}\n```\n")

            # Output
            if test_result['execution']['success']:
                lines.append("**Output:**")
                output = test_result['execution']['output']
                if len(output) > 500:
                    output = output[:500] + "\n... (truncated)"
                lines.append(f"```\n{output}\n```\n")

            # Category scores
            lines.append("#### Category Breakdown\n")

            cat_table = []
            for cat_name, cat_result in test_result['evaluation'].items():
                status = "✓" if cat_result['passed'] else "✗"
                cat_table.append([
                    status,
                    cat_name.replace('_', ' ').title(),
                    f"{cat_result['score']:.1f}",
                    f"{cat_result['weight']:.1f}",
                    cat_result['evaluator']
                ])

            lines.append(tabulate(
                cat_table,
                headers=['Status', 'Category', 'Score', 'Weight', 'Evaluator'],
                tablefmt='pipe'
            ))
            lines.append("")

            # Feedback
            lines.append("#### Detailed Feedback\n")
            for cat_name, cat_result in test_result['evaluation'].items():
                lines.append(f"**{cat_name.replace('_', ' ').title()}:**\n")
                lines.append("```")
                lines.append(cat_result['feedback'])
                lines.append("```\n")

            lines.append("---\n")

        # Recommendations
        lines.append("## 💡 Recommendations\n")
        lines.append(self._generate_recommendations())

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return filepath

    def _generate_recommendations(self) -> str:
        """Generate improvement recommendations"""
        recommendations = []

        # Analyze common failures
        all_evaluations = {}
        for test_result in self.results['test_results']:
            for cat_name, cat_result in test_result['evaluation'].items():
                if cat_name not in all_evaluations:
                    all_evaluations[cat_name] = []
                all_evaluations[cat_name].append(cat_result['score'])

        weak_categories = []
        for cat_name, scores in all_evaluations.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            if avg_score < 70:
                weak_categories.append((cat_name, avg_score))

        if weak_categories:
            weak_categories.sort(key=lambda x: x[1])
            recommendations.append("**Areas needing improvement:**\n")
            for cat_name, score in weak_categories:
                recommendations.append(f"- **{cat_name.replace('_', ' ').title()}** (avg: {score:.1f}/100)")

                # Specific suggestions
                if 'format' in cat_name.lower():
                    recommendations.append("  - Review output format requirements")
                    recommendations.append("  - Add explicit formatting instructions to prompt")
                elif 'completeness' in cat_name.lower():
                    recommendations.append("  - Ensure prompt explicitly requests all required elements")
                    recommendations.append("  - Consider adding a checklist in the prompt")
                elif 'accuracy' in cat_name.lower():
                    recommendations.append("  - Provide more context or examples in the prompt")
                    recommendations.append("  - Be more specific about requirements")
                elif 'clarity' in cat_name.lower():
                    recommendations.append("  - Request clearer, more structured output")
                    recommendations.append("  - Consider adding output format examples")
            recommendations.append("")

        if self.results['overall_score'] >= 90:
            recommendations.append("✨ **Excellent performance!** This prompt is production-ready.\n")
        elif self.results['overall_score'] >= 70:
            recommendations.append("✓ **Good performance.** Minor improvements could enhance consistency.\n")
        else:
            recommendations.append("⚠️ **Significant improvements needed.** Review and refine the prompt before production use.\n")

        return '\n'.join(recommendations)

    def get_summary(self) -> str:
        """Get colored terminal summary"""
        score = self.results['overall_score']

        if score >= 90:
            color = Fore.GREEN
            grade = "EXCELLENT"
        elif score >= 80:
            color = Fore.GREEN
            grade = "GOOD"
        elif score >= 70:
            color = Fore.YELLOW
            grade = "ACCEPTABLE"
        elif score >= 60:
            color = Fore.YELLOW
            grade = "NEEDS IMPROVEMENT"
        else:
            color = Fore.RED
            grade = "POOR"

        summary_lines = [
            f"{Fore.CYAN}PROMPT:{Style.RESET_ALL} {self.prompt_name}",
            f"{Fore.CYAN}OVERALL SCORE:{Style.RESET_ALL} {color}{score:.1f}/100{Style.RESET_ALL}",
            f"{Fore.CYAN}GRADE:{Style.RESET_ALL} {color}{grade}{Style.RESET_ALL}",
            f"{Fore.CYAN}PASS RATE:{Style.RESET_ALL} {self.results['pass_rate']:.1f}% ({self.results['passed_tests']}/{self.results['total_tests']} tests)",
        ]

        return '\n'.join(summary_lines)
