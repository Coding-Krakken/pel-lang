# PEL IDE Integration

IDE/editor extensions for PEL (Programmable Economic Language).

## Available Extensions

### Visual Studio Code
Full-featured extension with LSP support providing:
- Syntax highlighting
- Real-time diagnostics
- IntelliSense completion
- Hover documentation
- Go-to-definition
- Find references
- Document symbols
- Rename refactoring

**Installation:**
```bash
cd vscode
npm install
npm run package
code --install-extension pel-vscode-*.vsix
```

See [vscode/README.md](vscode/README.md) for details.

### Neovim (Coming Soon)
Configuration for nvim-lspconfig.

### Emacs (Coming Soon)
LSP client configuration.

## Language Server

All IDE integrations use the PEL Language Server Protocol (LSP) implementation.

**Start the LSP server:**
```bash
pip install -e ".[lsp]"
pel lsp
```

The server communicates via stdin/stdout following the LSP specification.

## Manual Configuration

If your editor supports LSP, you can configure it to use PEL:

**Server command:** `pel lsp`
**File extensions:** `.pel`

## Development

To test the LSP server:
```bash
# Terminal 1: Start server with logging
PEL_LSP_LOG=debug pel lsp 2> lsp.log

# Terminal 2: Send LSP messages via stdin
echo '{"jsonrpc":"2.0","id":1,"method":"initialize",...}' | pel lsp
```

## Contributing

Contributions for additional editor integrations are welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md).
