import * as path from 'path';
import { workspace, ExtensionContext } from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: ExtensionContext) {
    // Get PEL executable path from configuration
    const pelPath = workspace.getConfiguration('pel').get<string>('server.path') || 'pel';

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
    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
