"""
Configuration loader with template support
"""

from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    """Loads and merges configuration from templates and custom files"""

    def __init__(self, config_path: str = None, template: str = 'generic'):
        self.config_path = config_path
        self.template = template
        self.framework_dir = Path(__file__).parent.parent

    def load(self) -> dict[str, Any]:
        """Load configuration with template fallback"""
        # Start with template
        config = self._load_template()

        # Override with custom config if provided
        if self.config_path and Path(self.config_path).exists():
            custom_config = self._load_yaml(self.config_path)
            config = self._merge_configs(config, custom_config)

        return config

    def _load_template(self) -> dict[str, Any]:
        """Load template configuration"""
        template_path = self.framework_dir / 'config' / 'templates' / f'{self.template}.yaml'

        if template_path.exists():
            return self._load_yaml(template_path)

        # Fallback to generic template
        generic_path = self.framework_dir / 'config' / 'templates' / 'generic.yaml'
        if generic_path.exists():
            return self._load_yaml(generic_path)

        # Return default config
        return self._get_default_config()

    def _load_yaml(self, path: str) -> dict[str, Any]:
        """Load YAML file"""
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _merge_configs(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configurations"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _get_default_config(self) -> dict[str, Any]:
        """Return default configuration"""
        return {
            'version': '1.0',
            'pass_threshold': 70,
            'evaluation': {
                'format': {
                    'weight': 20,
                    'evaluator': 'regex',
                    'criteria': {
                        'must_match': [],
                        'must_not_match': [],
                        'threshold': 80
                    }
                },
                'completeness': {
                    'weight': 30,
                    'evaluator': 'checklist',
                    'criteria': {
                        'required_elements': [],
                        'optional_elements': [],
                        'threshold': 80
                    }
                },
                'quality': {
                    'weight': 50,
                    'evaluator': 'llm_judge',
                    'criteria': {
                        'rubric': 'Evaluate the overall quality, accuracy, and usefulness of the output.',
                        'aspects': ['accuracy', 'completeness', 'clarity'],
                        'threshold': 70
                    }
                }
            },
            'test_cases': []
        }
