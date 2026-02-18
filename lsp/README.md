# PEL Language Server Protocol (LSP)

This module implements the Language Server Protocol for PEL, enabling rich IDE integration.

## Status
✅ **Fully Implemented** - Complete LSP 3.17 implementation with all core features

## Implemented Features
- ✅ Real-time syntax diagnostics
- ✅ Semantic type checking
- ✅ Auto-completion for models, rates, parameters
- ✅ Hover documentation
- ✅ Go-to-definition
- ✅ Find references
- ✅ Symbol outline
- ✅ Code folding
- ✅ Rename refactoring

## Installation
```bash
pip install -e ".[lsp]"
```

## Usage
```bash
pel lsp
```

## IDE Integration
See `editors/` directory for VS Code, Neovim, and Emacs extensions.
