# PEL Language Support for VS Code

Rich language support for PEL (Programmable Economic Language) in Visual Studio Code.

## Features

- **Syntax Highlighting** - Full syntax highlighting for PEL source files
- **Real-time Diagnostics** - Syntax and semantic errors highlighted as you type
- **IntelliSense** - Auto-completion for keywords, types, parameters, and rates
- **Hover Documentation** - Hover over symbols to see type information and documentation
- **Go to Definition** - Jump to parameter and rate declarations
- **Find All References** - Find all uses of parameters and rates
- **Document Symbols** - Outline view of model structure
- **Rename Refactoring** - Rename parameters and rates across the file

## Requirements

- VS Code 1.75.0 or higher
- PEL compiler installed and available in PATH
  ```bash
  pip install -e ".[lsp]"
  ```

## Installation

### From VSIX (Recommended)
1. Download the latest `.vsix` file from releases
2. Open VS Code
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
4. Type "Install from VSIX" and select the downloaded file

### From Source
```bash
cd editors/vscode
npm install
npm run compile
npm run package  # Creates .vsix file
code --install-extension pel-vscode-*.vsix
```

## Configuration

The extension can be configured via VS Code settings:

- `pel.server.path` - Path to PEL executable (default: `"pel"`)
- `pel.trace.server` - Enable LSP message tracing for debugging

## Usage

1. Open any `.pel` file
2. The language server will start automatically
3. Enjoy features like auto-completion, diagnostics, and more!

## Example

```pel
model SaaS_Revenue {
  param monthly_price: Currency = 99 USD
    provenance {
      source: "Product pricing page"
      rationale: "Standard tier pricing"
    }
  
  param churn_rate: Rate = 0.05 per Month
  
  rate monthly_revenue: Currency per Month = 
    active_users * monthly_price
}
```

## Development

To work on the extension:

```bash
cd editors/vscode
npm install
npm run watch
```

Then press `F5` in VS Code to launch the extension development host.

## License

Dual-licensed under AGPL-3.0 or Commercial License.
See [LICENSE](../../LICENSE) and [COMMERCIAL-LICENSE.md](../../COMMERCIAL-LICENSE.md).
