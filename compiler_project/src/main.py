import sys
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .symbol_table import SymbolTable

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    # Read input file
    try:
        with open(sys.argv[1], 'r') as file:
            input_text = file.read()
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found")
        sys.exit(1)

    # Initialize components
    symbol_table = SymbolTable()
    lexer = Lexer()
    parser = Parser()
    semantic_analyzer = SemanticAnalyzer(symbol_table)

    # Lexical Analysis
    print("\n=== Lexical Analysis ===")
    lexer.input(input_text)
    while True:
        token = lexer.token()
        if not token:
            break
        print(f"Token: {token.type}, Value: {token.value}, Line: {token.lineno}, Position: {token.lexpos}")

    # Syntax Analysis
    print("\n=== Syntax Analysis ===")
    ast = parser.parse(input_text)
    if not ast:
        print("Syntax analysis failed")
        sys.exit(1)
    print("Syntax analysis successful")
    print("Abstract Syntax Tree:")
    print_ast(ast)

    # Semantic Analysis
    print("\n=== Semantic Analysis ===")
    if semantic_analyzer.analyze(ast):
        print("Semantic analysis successful")
    else:
        print("Semantic analysis failed")
        for error in semantic_analyzer.errors:
            print(error)
        sys.exit(1)

    # Symbol Table
    print("\n=== Symbol Table ===")
    print_symbol_table(symbol_table)

def print_ast(node, level=0):
    """Pretty print the AST."""
    indent = "  " * level
    if isinstance(node, tuple):
        print(f"{indent}{node[0]}")
        for child in node[1:]:
            print_ast(child, level + 1)
    elif isinstance(node, list):
        for item in node:
            print_ast(item, level)
    else:
        print(f"{indent}{node}")

def print_symbol_table(symbol_table):
    """Pretty print the symbol table."""
    print("Global Scope:")
    for (name, scope), symbol in symbol_table.symbols.items():
        if scope == "global":
            print(f"  {name}: {symbol.type}")
    
    print("\nLocal Scopes:")
    scopes = set(scope for _, scope in symbol_table.symbols.keys()) - {"global"}
    for scope in sorted(scopes):
        print(f"\n{scope}:")
        for (name, sym_scope), symbol in symbol_table.symbols.items():
            if sym_scope == scope:
                print(f"  {name}: {symbol.type}")

if __name__ == "__main__":
    main() 