# PEL Formatter

This module provides automatic code formatting for PEL source files.

## Status
✅ **Available** - Formatting is implemented with token-aware spacing and indentation.

**Current Limitations:**
- Line wrapping for overly long statements is best-effort (some lines >100 chars may remain)
- Block comment formatting is not yet supported (line comments `//` work correctly)
- No auto-import organization (future feature)

## Formatter Features
- Consistent indentation (default: 4 spaces)
- Operator spacing and comma normalization
- Brace-based block indentation
- Comment preservation (line comments)
- Configurable line length and indent size

## Installation
```bash
pip install -e ".[dev]"
```

## Usage

### Format Code
```bash
pel format mymodel.pel
pel format --check mymodel.pel
pel format --diff mymodel.pel
pel format src/

# Convenience entrypoint
pelformat mymodel.pel
```

## Configuration
Create a `.pelformat.toml` file in your repo:

```toml
[format]
line_length = 100
indent_size = 4
```

## Notes
- Formatting is whitespace-only and does not alter semantics.
- Line wrapping is best-effort; very long expressions may remain unchanged.
