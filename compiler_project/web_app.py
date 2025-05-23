from flask import Flask, render_template, request
import io
import sys
from contextlib import redirect_stdout
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.symbol_table import SymbolTable

app = Flask(__name__)

# Example program for initial display
EXAMPLE_PROGRAM = """// Example program
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

void main(void) {
    int number;
    int result;
    number = 5;
    result = factorial(number);
}"""

def format_ast(node, level=0):
    """Format AST node with HTML classes for better visualization."""
    indent = "&nbsp;" * (4 * level)
    if isinstance(node, tuple):
        node_type = node[0]
        # Add special styling for error nodes
        is_error = 'error' in node_type
        node_class = 'node-error' if is_error else 'node'
        result = [f'<div class="{node_class}"><div class="node-content">{indent}{node_type}</div>']
        for child in node[1:]:
            result.append(format_ast(child, level + 1))
        result.append('</div>')
        return '\n'.join(result)
    elif isinstance(node, list):
        result = []
        for item in node:
            result.append(format_ast(item, level))
        return '\n'.join(result)
    else:
        return f'<div class="node"><div class="node-content">{indent}{node}</div></div>'

def format_symbol_table(symbol_table):
    """Format symbol table data for structured display."""
    scopes = []
    
    # Global scope
    global_symbols = []
    for (name, scope), symbol in symbol_table.symbols.items():
        if scope == "global":
            global_symbols.append({
                'name': name,
                'type': symbol.type,
                'attributes': ', '.join(f'{k}: {v}' for k, v in symbol.attributes.items())
            })
    
    if global_symbols:
        scopes.append({
            'name': 'Global Scope',
            'symbols': global_symbols
        })
    
    # Local scopes
    local_scopes = set(scope for _, scope in symbol_table.symbols.keys()) - {"global"}
    for scope in sorted(local_scopes):
        scope_symbols = []
        for (name, sym_scope), symbol in symbol_table.symbols.items():
            if sym_scope == scope:
                scope_symbols.append({
                    'name': name,
                    'type': symbol.type,
                    'attributes': ', '.join(f'{k}: {v}' for k, v in symbol.attributes.items())
                })
        
        if scope_symbols:
            scopes.append({
                'name': f'Scope: {scope}',
                'symbols': scope_symbols
            })
    
    return scopes

@app.route('/', methods=['GET', 'POST'])
def index():
    code = EXAMPLE_PROGRAM
    results = None

    if request.method == 'POST':
        code = request.form.get('code', '')
        results = {}
        
        # Initialize components
        symbol_table = SymbolTable()
        lexer = Lexer()
        parser = Parser()
        semantic_analyzer = SemanticAnalyzer(symbol_table)

        # Lexical Analysis
        tokens = []
        lexer.input(code)
        while True:
            token = lexer.token()
            if not token:
                break
            tokens.append({
                'type': token.type,
                'value': token.value,
                'line': token.lineno,
                'position': token.lexpos
            })
        results['tokens'] = tokens

        # Syntax Analysis
        ast = parser.parse(code)
        results['syntax_success'] = len(parser.errors) == 0
        results['syntax_errors'] = parser.errors
        if ast:
            results['syntax_analysis'] = format_ast(ast)
        else:
            results['syntax_analysis'] = "Syntax analysis failed"

        # Semantic Analysis
        if ast:  # Only perform semantic analysis if syntax analysis succeeded
            semantic_success = semantic_analyzer.analyze(ast)
            results['semantic_success'] = semantic_success
            results['semantic_errors'] = semantic_analyzer.errors
            def format_semantic_result():
                if semantic_success:
                    print("✓ Semantic analysis successful")
                else:
                    print("✗ Semantic analysis failed")
                    for error in semantic_analyzer.errors:
                        print(f"• {error}")

            results['semantic_analysis'] = capture_output(format_semantic_result)
        else:
            results['semantic_success'] = False
            results['semantic_analysis'] = "Semantic analysis skipped due to syntax errors"
            results['semantic_errors'] = []

        # Symbol Table
        results['symbol_table'] = format_symbol_table(symbol_table)

    return render_template('index.html', code=code, results=results)

def capture_output(func):
    """Capture stdout output from a function."""
    output = io.StringIO()
    with redirect_stdout(output):
        func()
    return output.getvalue()

if __name__ == '__main__':
    app.run(debug=True) 