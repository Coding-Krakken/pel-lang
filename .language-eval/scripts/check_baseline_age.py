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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

DEFAULT_WARNING_DAYS = 90
DEFAULT_ERROR_DAYS = 180


def _load_baseline(path: Path) -> dict[str, Any]:
    """Load baseline JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON in {path}: {exc}"
        logger.exception("Failed to load baseline JSON")
        raise SystemExit(msg) from exc
    except FileNotFoundError as exc:
        msg = f"Baseline not found: {path}"
        logger.exception("Baseline file not found")
        raise SystemExit(msg) from exc


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
        logger.warning("Baseline %s has no created_at or generated_at timestamp", baseline_path.name)
        return 1

    try:
        # Try ISO format first
        if "T" in created_at_str:
            created_at = dt.datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).date()
        else:
            created_at = dt.date.fromisoformat(created_at_str)
    except ValueError as exc:
        msg = f"Invalid date format in baseline: {created_at_str}"
        logger.exception("Failed to parse baseline date")
        raise SystemExit(msg) from exc
    
    age_days = (today - created_at).days

    logger.info("Baseline: %s", baseline_path.name)
    logger.info("  Created: %s", created_at)
    logger.info("  Age: %d days", age_days)
    logger.info("  Target ID: %s", baseline.get("target_id", "unknown"))

    if age_days >= error_days:
        logger.error("  ❌ CRITICAL: Baseline is %d days old (>= %d day threshold)", age_days, error_days)
        logger.error("  Action required: Update baseline or extend retention policy")
        return 2
    elif age_days >= warning_days:
        logger.warning("  ⚠️  WARNING: Baseline is %d days old (>= %d day threshold)", age_days, warning_days)
        logger.warning("  Recommended: Review baseline for relevance")
        return 1
    else:
        logger.info("  ✅ OK: Baseline is fresh (%d days old)", age_days)
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
        logger.info("✅ All baselines are fresh")
        return 0
    elif max_status == 1:
        logger.warning("⚠️  Some baselines need review")
        return 1 if args.fail_on_warning else 0
    else:
        logger.error("❌ Some baselines are critically stale")
        return 2


if __name__ == "__main__":
    sys.exit(main())
