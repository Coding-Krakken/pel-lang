#!/usr/bin/env python3
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Check baseline age and warn if baselines are stale."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

DEFAULT_WARNING_DAYS = 90
DEFAULT_ERROR_DAYS = 180


def _load_baseline(path: Path) -> dict[str, Any]:
    """Load baseline JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logging.error(f"Invalid JSON in {path}: {exc}")
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        logging.error(f"Baseline not found: {path}")
        raise SystemExit(f"Baseline not found: {path}") from exc


def check_baseline_age(
    baseline_path: Path,
    warning_days: int,
    error_days: int,
    today: dt.date | None = None,
) -> int:
    """
    Check baseline age and return appropriate exit code.
    
    Returns:
        0: Baseline is fresh (< warning_days)
        1: Baseline is stale (>= warning_days, < error_days) - WARNING
        2: Baseline is very stale (>= error_days) - ERROR
    """
    if today is None:
        today = dt.date.today()
    
    baseline = _load_baseline(baseline_path)
    
    # Try to extract creation date from baseline
    created_at_str = baseline.get("created_at", baseline.get("generated_at", ""))
    
    if not created_at_str:
        logging.warning(f"Baseline {baseline_path.name} has no created_at or generated_at timestamp")
        return 1
    
    try:
        # Try ISO format first
        if "T" in created_at_str:
            created_at = dt.datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).date()
        else:
            created_at = dt.date.fromisoformat(created_at_str)
    except ValueError as exc:
        logging.error(f"Invalid date format in baseline: {created_at_str}")
        raise SystemExit(f"Invalid date format in baseline: {created_at_str}") from exc
    
    age_days = (today - created_at).days
    
    logging.info(f"Baseline: {baseline_path.name}")
    logging.info(f"  Created: {created_at}")
    logging.info(f"  Age: {age_days} days")
    logging.info(f"  Target ID: {baseline.get('target_id', 'unknown')}")
    
    if age_days >= error_days:
        logging.error(f"  ❌ CRITICAL: Baseline is {age_days} days old (>= {error_days} day threshold)")
        logging.error(f"  Action required: Update baseline or extend retention policy")
        return 2
    elif age_days >= warning_days:
        logging.warning(f"  ⚠️  WARNING: Baseline is {age_days} days old (>= {warning_days} day threshold)")
        logging.warning(f"  Recommended: Review baseline for relevance")
        return 1
    else:
        logging.info(f"  ✅ OK: Baseline is fresh ({age_days} days old)")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baselines", nargs="+", help="Baseline JSON files to check")
    parser.add_argument(
        "--warning-days",
        type=int,
        default=DEFAULT_WARNING_DAYS,
        help=f"Warn if baseline older than N days (default: {DEFAULT_WARNING_DAYS})",
    )
    parser.add_argument(
        "--error-days",
        type=int,
        default=DEFAULT_ERROR_DAYS,
        help=f"Error if baseline older than N days (default: {DEFAULT_ERROR_DAYS})",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with code 1 on warnings (not just errors)",
    )
    parser.add_argument(
        "--today",
        help="Override today's date for testing (ISO format YYYY-MM-DD)",
    )
    args = parser.parse_args()
    
    today = dt.date.fromisoformat(args.today) if args.today else None
    
    max_status = 0
    for baseline_file in args.baselines:
        baseline_path = Path(baseline_file)
        status = check_baseline_age(baseline_path, args.warning_days, args.error_days, today)
        max_status = max(max_status, status)
        print()  # Blank line between baselines
    
    # Summary
    if max_status == 0:
        logging.info("✅ All baselines are fresh")
        return 0
    elif max_status == 1:
        logging.warning("⚠️  Some baselines need review")
        return 1 if args.fail_on_warning else 0
    else:
        logging.error("❌ Some baselines are critically stale")
        return 2


if __name__ == "__main__":
    sys.exit(main())
