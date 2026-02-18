# PEL Formatter & Linter

This module provides code quality tools for PEL:
- **Formatter** (`pelformat`) - Automatic code formatting
- **Linter** (`pellint`) - Static analysis and best practices

## Status
🚧 **In Development** - See PR-21 for implementation roadmap

## Formatter Features
- ✅ Consistent indentation (4 spaces)
- ✅ Line wrapping (100 character limit)
- ✅ Operator spacing
- ✅ Block alignment (models, rates, parameters)
- ✅ Comment formatting
- ✅ Import sorting

## Linter Rules
- ✅ **PEL001**: Unused parameter
- ✅ **PEL002**: Unreferenced rate
- ✅ **PEL003**: Invalid semantic contract
- ✅ **PEL004**: Type mismatch
- ✅ **PEL005**: Circular dependency
- ✅ **PEL006**: Missing documentation
- ✅ **PEL007**: Anti-pattern detected

## Installation
```bash
pip install -e ".[dev]"
```

## Usage

### Format Code
```bash
# Format file in-place
pel format mymodel.pel

# Check formatting (dry-run)
pel format --check mymodel.pel

# Format entire directory
pel format src/
```

### Lint Code
```bash
# Lint file
pel lint mymodel.pel

# Lint with JSON output (for CI)
pel lint --json mymodel.pel

# Lint entire directory
pel lint src/
```

## Editor Integration
- **VS Code**: Formatter runs on save (requires LSP extension)
- **pre-commit**: Add to `.pre-commit-config.yaml`
