import { workspace, ExtensionContext, window } from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';
import { execSync } from 'child_process';

let client: LanguageClient;

/**
 * Check if a command is available in the system PATH
 */
function commandExists(command: string): boolean {
    try {
        execSync(`${command} --version`, { stdio: 'ignore' });
        return true;
    } catch (error) {
        return false;
    }
}

export function activate(context: ExtensionContext): void {
    // Get PEL executable path from configuration
    const pelPath = workspace.getConfiguration('pel').get<string>('server.path') || 'pel';

    // Verify PEL is installed
    if (!commandExists(pelPath)) {
        const message = `PEL command '${pelPath}' not found. Please install PEL with LSP support: pip install -e ".[lsp]"`;
        window.showErrorMessage(message);
        console.error(message);
        return;
    }

    // Server is started via the PEL CLI
    const serverOptions: ServerOptions = {
        command: pelPath,
        args: ['lsp'],
        options: {}
    };

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for PEL documents
        documentSelector: [{ scheme: 'file', language: 'pel' }],
        synchronize: {
            // Notify the server about file changes to '.pel' files contained in the workspace
            fileEvents: workspace.createFileSystemWatcher('**/*.pel')
        }
    };

    // Create the language client
    client = new LanguageClient(
        'pelLanguageServer',
        'PEL Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client (this will also launch the server)
    client.start().catch((error) => {
        const message = `Failed to start PEL Language Server: ${error.message}`;
        window.showErrorMessage(message);
        console.error(message, error);
    });

    console.log('PEL Language Server extension activated');
}

export function deactivate(): Promise<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

