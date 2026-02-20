#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Validate all baseline files against expected schema structure."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


REQUIRED_BASELINE_FIELDS = [
    "target_id",
    "overall_score",
    "category_scores",
]

OPTIONAL_BASELINE_FIELDS = [
    "created_at",
    "generated_at",
    "version",
    "environment",
    "suite_scores",
    "weights",
]


def validate_baseline(baseline_path: Path) -> tuple[bool, list[str]]:
    """
    Validate a single baseline file.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors: list[str] = []
    
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {exc}")
        return False, errors
    except FileNotFoundError:
        errors.append("File not found")
        return False, errors
    
    # Check required fields
    for field in REQUIRED_BASELINE_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate overall_score range
    if "overall_score" in data:
        score = data["overall_score"]
        if not isinstance(score, (int, float)):
            errors.append(f"overall_score must be numeric, got {type(score).__name__}")
        elif not 0.0 <= score <= 5.0:
            errors.append(f"overall_score must be in range [0.0, 5.0], got {score}")
    
    # Validate category_scores
    if "category_scores" in data:
        cat_scores = data["category_scores"]
        if not isinstance(cat_scores, dict):
            errors.append(f"category_scores must be object/dict, got {type(cat_scores).__name__}")
        else:
            for category, score in cat_scores.items():
                if not isinstance(score, (int, float)):
                    errors.append(f"category_scores.{category} must be numeric, got {type(score).__name__}")
                elif not 0.0 <= score <= 5.0:
                    errors.append(f"category_scores.{category} must be in range [0.0, 5.0], got {score}")
    
    # Check for timestamp
    has_timestamp = "created_at" in data or "generated_at" in data
    if not has_timestamp:
        errors.append("Missing timestamp field (should have created_at or generated_at)")
    
    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baselines", nargs="+", help="Baseline JSON files to validate")
    parser.add_argument("--strict", action="store_true", help="Exit with error on any validation failure")
    args = parser.parse_args()
    
    total_files = 0
    valid_files = 0
    invalid_files = 0
    
    for baseline_file in args.baselines:
        baseline_path = Path(baseline_file)
        total_files += 1
        
        logger.info("Validating: %s", baseline_path.name)
        is_valid, errors = validate_baseline(baseline_path)
        
        if is_valid:
            logger.info("  ✅ Valid")
            valid_files += 1
        else:
            logger.error("  ❌ Invalid:")
            for error in errors:
                logger.error("    - %s", error)
            invalid_files += 1
        
        print()  # Blank line between files
    
    # Summary
    logger.info("=" * 60)
    logger.info("Validation Summary:")
    logger.info("  Total files: %d", total_files)
    logger.info("  Valid: %d", valid_files)
    logger.info("  Invalid: %d", invalid_files)
    
    if invalid_files > 0:
        if args.strict:
            logger.error("❌ Validation failed (strict mode)")
            return 1
        else:
            logger.warning("⚠️  Some baselines have validation errors")
            return 0
    else:
        logger.info("✅ All baselines are valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
