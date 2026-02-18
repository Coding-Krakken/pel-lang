# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL linter package."""

from linter.config import LinterConfig, load_linter_config
from linter.linter import PELLinter

__all__ = ["LinterConfig", "PELLinter", "load_linter_config"]
__version__ = "0.2.0"
