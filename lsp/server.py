"""
PEL LSP Server
Main entry point for the Language Server Protocol implementation.
"""

import logging
import re

# Import PEL compiler components
import sys
from pathlib import Path

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_RENAME,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    DefinitionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    HoverParams,
    Location,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    ReferenceParams,
    RenameParams,
    SymbolKind,
    TextEdit,
    WorkspaceEdit,
)
from pygls.protocol import LanguageServerProtocol
from pygls.server import JsonRPCServer

sys.path.insert(0, str(Path(__file__).parent.parent))

from compiler.ast_nodes import Model
from compiler.errors import CompilerError
from compiler.lexer import Lexer, Token
from compiler.parser import Parser
from compiler.typechecker import TypeChecker

logger = logging.getLogger(__name__)


class PELLanguageServerProtocol(LanguageServerProtocol):
    """Custom protocol for PEL language server."""

    def __init__(self, server, converter):
        super().__init__(server, converter)
        self._server_instance = server


class PELLanguageServer(JsonRPCServer):
    """
    Language Server Protocol implementation for PEL.

    Provides IDE integration capabilities including diagnostics,
    completion, hover, go-to-definition, and more.
    """

    def __init__(self):
        self.name = "pel-language-server"
        self.version = "0.1.0"
        super().__init__(
            protocol_cls=lambda server, converter: PELLanguageServerProtocol(server, converter),
            converter_factory=lambda: None  # Use default cattrs converter
        )
        self.lsp = self.protocol
        self.document_asts = {}  # Cache parsed ASTs per document
        self.document_tokens = {}  # Cache tokens per document
        self.document_symbols = {}  # Cache symbols per document


# Create global server instance
server = PELLanguageServer()


def parse_document(source: str) -> tuple[Model | None, list[Token], list[Diagnostic]]:
    """
    Parse PEL source and return AST, tokens, and diagnostics.

    Returns:
        (ast, tokens, diagnostics)
    """
    diagnostics = []
    ast = None
    tokens = []

    try:
        # Lexical analysis
        lexer = Lexer(source, filename="<lsp-document>")
        tokens = lexer.tokenize()

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        # Type checking
        type_checker = TypeChecker()
        ast = type_checker.check_model(ast)

        # Collect errors if any
        if type_checker.has_errors():
            for error in type_checker.get_errors():
                diagnostics.append(compiler_error_to_diagnostic(error))

        # Collect warnings
        for warning in type_checker.get_warnings():
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=0)
                ),
                message=warning,
                severity=DiagnosticSeverity.Warning,
                source="pel-typechecker"
            ))

    except CompilerError as e:
        diagnostics.append(compiler_error_to_diagnostic(e))
    except Exception as e:
        # Catch-all for unexpected errors
        diagnostics.append(Diagnostic(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            ),
            message=f"Internal error: {str(e)}",
            severity=DiagnosticSeverity.Error,
            source="pel-lsp"
        ))
        logger.exception("Unexpected error during parsing")

    return ast, tokens, diagnostics


def compiler_error_to_diagnostic(error: CompilerError) -> Diagnostic:
    """Convert PEL compiler error to LSP diagnostic."""
    # Extract line/column from error location if available
    line = 0
    character = 0

    if error.location:
        line = max(0, error.location.line - 1)  # LSP uses 0-based lines
        character = max(0, error.location.column - 1)  # LSP uses 0-based columns

    # Create range (single position if we don't have more info)
    diagnostic_range = Range(
        start=Position(line=line, character=character),
        end=Position(line=line, character=character + 10)  # Approximate end
    )

    # Format message with error code
    message = f"{error.code}: {error.message}"
    if error.hint:
        message += f"\n💡 {error.hint}"

    return Diagnostic(
        range=diagnostic_range,
        message=message,
        severity=DiagnosticSeverity.Error,
        code=error.code,
        source="pel-compiler"
    )


def extract_symbols(ast: Model) -> list[DocumentSymbol]:
    """Extract document symbols from AST."""
    symbols = []

    if not ast:
        return symbols

    # Model declaration
    model_symbol = DocumentSymbol(
        name=ast.name,
        kind=SymbolKind.Module,
        range=Range(
            start=Position(line=0, character=0),
            end=Position(line=999, character=0)
        ),
        selection_range=Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=10)
        ),
        children=[]
    )

    # Parameters
    for param in ast.params:
        param_symbol = DocumentSymbol(
            name=param.name,
            kind=SymbolKind.Variable,
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=10)
            ),
            selection_range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=10)
            ),
            detail=f"{param.type_annotation.type_kind}" if param.type_annotation else "Parameter"
        )
        model_symbol.children.append(param_symbol)

    # Variables (rates, etc.)
    for var in ast.vars:
        var_symbol = DocumentSymbol(
            name=var.name,
            kind=SymbolKind.Function,
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=10)
            ),
            selection_range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=10)
            ),
            detail=f"{var.type_annotation.type_kind}" if var.type_annotation else "Variable"
        )
        model_symbol.children.append(var_symbol)

    symbols.append(model_symbol)
    return symbols


def get_hover_info(ast: Model, position: Position, source: str) -> str | None:
    """Get hover information for position in document."""
    if not ast:
        return None

    # Get the word at position
    lines = source.split('\n')
    if position.line >= len(lines):
        return None

    line = lines[position.line]
    if position.character >= len(line):
        return None

    # Extract word at cursor
    start = position.character
    end = position.character

    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1

    word = line[start:end]

    if not word:
        return None

    # Look up in model
    # Check parameters
    for param in ast.params:
        if param.name == word:
            info = f"**Parameter:** `{param.name}`\n\n"
            if param.type_annotation:
                info += f"**Type:** `{param.type_annotation.type_kind}`\n\n"
            if hasattr(param, 'value') and param.value:
                info += f"**Default:** `{param.value}`\n\n"
            if hasattr(param, 'provenance') and param.provenance:
                info += f"**Provenance:** {param.provenance.source}\n\n"
                if param.provenance.rationale:
                    info += f"**Rationale:** {param.provenance.rationale}\n\n"
            return info

    # Check variables
    for var in ast.vars:
        if var.name == word:
            info = f"**Variable:** `{var.name}`\n\n"
            if var.type_annotation:
                info += f"**Type:** `{var.type_annotation.type_kind}`\n\n"
            return info

    # Check built-in types
    builtin_types = {
        "Currency": "Represents monetary values with currency tracking",
        "Rate": "Represents ratios and percentages",
        "Duration": "Represents time intervals",
        "Count": "Represents quantities of discrete entities",
        "Capacity": "Represents maximum throughput or limits",
        "Fraction": "Represents dimensionless ratios (0-1)",
        "TimeSeries": "Represents values that vary over time",
        "Distribution": "Represents probability distributions for uncertainty modeling",
        "Boolean": "Boolean true/false values",
        "Array": "Array/list of values"
    }

    if word in builtin_types:
        return f"**Type:** `{word}`\n\n{builtin_types[word]}"

    # Check keywords
    keywords = {
        "model": "Defines a PEL model",
        "param": "Declares a model parameter",
        "rate": "Declares a rate/metric",
        "constraint": "Defines a constraint on values",
        "mechanism": "Defines a business mechanism/policy",
        "provenance": "Documents data source and rationale",
        "for": "Loop construct",
        "if": "Conditional construct",
        "Normal": "Normal/Gaussian distribution",
        "Uniform": "Uniform distribution",
        "Beta": "Beta distribution"
    }

    if word in keywords:
        return f"**Keyword:** `{word}`\n\n{keywords[word]}"

    return None


def get_completions(ast: Model, position: Position, source: str) -> list[CompletionItem]:
    """Get completion items at position."""
    completions = []

    # Keywords
    keywords = [
        "model", "param", "rate", "constraint", "mechanism", "provenance",
        "for", "if", "else", "in", "return"
    ]
    for kw in keywords:
        completions.append(CompletionItem(
            label=kw,
            kind=CompletionItemKind.Keyword,
            detail="PEL keyword"
        ))

    # Types
    types = [
        "Currency", "Rate", "Duration", "Count", "Capacity", "Fraction",
        "TimeSeries", "Distribution", "Boolean", "Array", "String", "Int"
    ]
    for t in types:
        completions.append(CompletionItem(
            label=t,
            kind=CompletionItemKind.Class,
            detail="PEL type"
        ))

    # Distributions
    distributions = ["Normal", "Uniform", "Beta", "LogNormal"]
    for d in distributions:
        completions.append(CompletionItem(
            label=d,
            kind=CompletionItemKind.Function,
            detail="Distribution"
        ))

    # From AST
    if ast:
        # Parameters
        for param in ast.params:
            completions.append(CompletionItem(
                label=param.name,
                kind=CompletionItemKind.Variable,
                detail=f"Parameter: {param.type_annotation.type_kind if param.type_annotation else 'unknown'}"
            ))

        # Variables
        for var in ast.vars:
            completions.append(CompletionItem(
                label=var.name,
                kind=CompletionItemKind.Function,
                detail=f"Variable: {var.type_annotation.type_kind if var.type_annotation else 'unknown'}"
            ))

    # Stdlib functions
    stdlib_functions = [
        "sum", "avg", "min", "max", "count", "concat",
        "clamp", "floor", "ceil", "round", "abs", "sqrt", "pow"
    ]
    for fn in stdlib_functions:
        completions.append(CompletionItem(
            label=fn,
            kind=CompletionItemKind.Function,
            detail="Built-in function"
        ))

    return completions


def find_definition_location(ast: Model, position: Position, source: str, uri: str) -> Location | None:
    """Find definition location for symbol at position."""
    if not ast:
        return None

    lines = source.split('\n')
    if position.line >= len(lines):
        return None

    line = lines[position.line]
    if position.character >= len(line):
        return None

    # Extract word at cursor
    start = position.character
    end = position.character

    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1

    word = line[start:end]

    if not word:
        return None

    # Search for definition in AST
    # This is simplified - in a real implementation, we'd track source positions in AST nodes
    for param in ast.params:
        if param.name == word:
            # Return approximate location (would need actual source positions in AST)
            return Location(
                uri=uri,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=10)
                )
            )

    for var in ast.vars:
        if var.name == word:
            return Location(
                uri=uri,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=10)
                )
            )

    return None


def find_references(ast: Model, position: Position, source: str, uri: str) -> list[Location]:
    """Find all references to symbol at position."""
    if not ast:
        return []

    lines = source.split('\n')
    if position.line >= len(lines):
        return []

    line = lines[position.line]
    if position.character >= len(line):
        return []

    # Extract word at cursor
    start = position.character
    end = position.character

    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1

    word = line[start:end]

    if not word:
        return []

    # Find all occurrences in source
    locations = []
    pattern = r'\b' + re.escape(word) + r'\b'

    for line_num, line_text in enumerate(lines):
        for match in re.finditer(pattern, line_text):
            locations.append(Location(
                uri=uri,
                range=Range(
                    start=Position(line=line_num, character=match.start()),
                    end=Position(line=line_num, character=match.end())
                )
            ))

    return locations


# LSP Event Handlers

@server.lsp.fm.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: PELLanguageServerProtocol, params: DidOpenTextDocumentParams):
    """Handle document open event."""
    uri = params.text_document.uri
    source = params.text_document.text

    # Parse document
    ast, tokens, diagnostics = parse_document(source)

    # Cache results - access server via ls._server_instance
    srv = ls._server_instance
    srv.document_asts[uri] = ast
    srv.document_tokens[uri] = tokens
    if ast:
        srv.document_symbols[uri] = extract_symbols(ast)

    # Publish diagnostics
    ls.publish_diagnostics(uri, diagnostics)


@server.lsp.fm.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: PELLanguageServerProtocol, params: DidChangeTextDocumentParams):
    """Handle document change event."""
    uri = params.text_document.uri

    # Get updated content (full sync)
    source = params.content_changes[0].text

    # Re-parse document
    ast, tokens, diagnostics = parse_document(source)

    # Update cache
    srv = ls._server_instance
    srv.document_asts[uri] = ast
    srv.document_tokens[uri] = tokens
    if ast:
        srv.document_symbols[uri] = extract_symbols(ast)

    # Publish updated diagnostics
    ls.publish_diagnostics(uri, diagnostics)


@server.lsp.fm.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: PELLanguageServerProtocol, params: DidCloseTextDocumentParams):
    """Handle document close event."""
    uri = params.text_document.uri

    # Clear cache
    srv = ls._server_instance
    srv.document_asts.pop(uri, None)
    srv.document_tokens.pop(uri, None)
    srv.document_symbols.pop(uri, None)


@server.lsp.fm.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: PELLanguageServerProtocol, params: CompletionParams) -> CompletionList:
    """Provide completion items."""
    uri = params.text_document.uri
    position = params.position

    # Get document from workspace
    document = ls.workspace.get_text_document(uri)
    ast = ls._server_instance.document_asts.get(uri)

    items = get_completions(ast, position, document.source)

    return CompletionList(is_incomplete=False, items=items)


@server.lsp.fm.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: PELLanguageServerProtocol, params: HoverParams) -> Hover | None:
    """Provide hover information."""
    uri = params.text_document.uri
    position = params.position

    document = ls.workspace.get_text_document(uri)
    ast = ls._server_instance.document_asts.get(uri)

    info = get_hover_info(ast, position, document.source)

    if info:
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=info),
            range=Range(
                start=position,
                end=Position(line=position.line, character=position.character + 10)
            )
        )

    return None


@server.lsp.fm.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: PELLanguageServerProtocol, params: DefinitionParams) -> Location | None:
    """Provide go-to-definition."""
    uri = params.text_document.uri
    position = params.position

    document = ls.workspace.get_text_document(uri)
    ast = ls._server_instance.document_asts.get(uri)

    return find_definition_location(ast, position, document.source, uri)


@server.lsp.fm.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: PELLanguageServerProtocol, params: ReferenceParams) -> list[Location]:
    """Find all references."""
    uri = params.text_document.uri
    position = params.position

    document = ls.workspace.get_text_document(uri)
    ast = ls._server_instance.document_asts.get(uri)

    return find_references(ast, position, document.source, uri)


@server.lsp.fm.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(ls: PELLanguageServerProtocol, params: DocumentSymbolParams) -> list[DocumentSymbol]:
    """Provide document symbols."""
    uri = params.text_document.uri
    return ls._server_instance.document_symbols.get(uri, [])


@server.lsp.fm.feature(TEXT_DOCUMENT_RENAME)
def rename(ls: PELLanguageServerProtocol, params: RenameParams) -> WorkspaceEdit | None:
    """Provide rename refactoring."""
    uri = params.text_document.uri
    position = params.position
    new_name = params.new_name

    document = ls.workspace.get_text_document(uri)
    ast = ls._server_instance.document_asts.get(uri)

    # Find all references
    refs = find_references(ast, position, document.source, uri)

    if not refs:
        return None

    # Create text edits for all references
    edits = [TextEdit(range=loc.range, new_text=new_name) for loc in refs]

    return WorkspaceEdit(changes={uri: edits})


def start():
    """Start the LSP server."""
    import logging

    from pygls import run

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('/tmp/pel-lsp.log'), logging.StreamHandler()]
    )

    logger.info("Starting PEL Language Server...")

    # Start server via stdio using the pygls run function
    run(server)


if __name__ == "__main__":
    start()
