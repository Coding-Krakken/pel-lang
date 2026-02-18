"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode_1 = require("vscode");
const node_1 = require("vscode-languageclient/node");
const child_process_1 = require("child_process");
let client;
/**
 * Check if a command is available in the system PATH
 */
function commandExists(command) {
    try {
        (0, child_process_1.execSync)(`${command} --version`, { stdio: 'ignore' });
        return true;
    }
    catch (error) {
        return false;
    }
}
function activate(context) {
    // Get PEL executable path from configuration
    const pelPath = vscode_1.workspace.getConfiguration('pel').get('server.path') || 'pel';
    // Verify PEL is installed
    if (!commandExists(pelPath)) {
        const message = `PEL command '${pelPath}' not found. Please install PEL with LSP support: pip install -e ".[lsp]"`;
        vscode_1.window.showErrorMessage(message);
        console.error(message);
        return;
    }
    // Server is started via the PEL CLI
    const serverOptions = {
        command: pelPath,
        args: ['lsp'],
        options: {}
    };
    // Options to control the language client
    const clientOptions = {
        // Register the server for PEL documents
        documentSelector: [{ scheme: 'file', language: 'pel' }],
        synchronize: {
            // Notify the server about file changes to '.pel' files contained in the workspace
            fileEvents: vscode_1.workspace.createFileSystemWatcher('**/*.pel')
        }
    };
    // Create the language client
    client = new node_1.LanguageClient('pelLanguageServer', 'PEL Language Server', serverOptions, clientOptions);
    // Start the client (this will also launch the server)
    client.start().catch((error) => {
        const message = `Failed to start PEL Language Server: ${error.message}`;
        vscode_1.window.showErrorMessage(message);
        console.error(message, error);
    });
    console.log('PEL Language Server extension activated');
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map