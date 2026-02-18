# PEL Linter

Static analysis for PEL code quality and best practices.

## Status
✅ **Available** - Core lint rules and JSON/text reporting are implemented.

## Rules
- PEL001: Unused parameter
- PEL002: Unreferenced variable
- PEL004: Type mismatch (typechecker-backed)
- PEL005: Circular dependency
- PEL008: Style violations (line length, trailing whitespace)
- PEL010: Naming conventions

## Usage
```bash
pel lint model.pel
pel lint --json model.pel
pel lint src/

# Convenience entrypoint
pellint model.pel
```

## Configuration
Create a `.pellint.toml` file in your repo:

```toml
[linter]
line_length = 100
enabled_rules = ["PEL001", "PEL002", "PEL004", "PEL005", "PEL008", "PEL010"]

[rules.PEL010]
severity = "info"
```
