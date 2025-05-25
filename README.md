# C-Like Language Compiler Project

A comprehensive compiler implementation for a C-like programming language that demonstrates the core concepts of compiler design including lexical analysis, syntax analysis, semantic analysis, and symbol table management.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [Team Members and Contributions](#team-members-and-contributions)

## Features

### 1. Lexical Analysis (Scanner)
- Token recognition for:
  - Keywords (if, else, while, return, void, int, float, char, boolean)
  - Operators (arithmetic, relational, logical)
  - Identifiers and literals
  - Comments and whitespace handling
  - Line number tracking for error reporting

### 2. Syntax Analysis (Parser)
- Recursive descent parser implementation
- Grammar rules for:
  - Variable and function declarations
  - Control structures (if-else, while)
  - Expressions and statements
  - Arrays and compound statements
- Advanced error detection:
  - Brace matching validation
  - Missing semicolon detection
  - Detailed syntax error reporting

### 3. Symbol Table Management
- Multi-level symbol table implementation
- Features:
  - Scope management (global/local)
  - Variable tracking
  - Function signature validation
  - Type checking support
  - Array dimension tracking
  - Line number recording
- Error Detection:
  - Duplicate declarations
  - Undefined variables
  - Type mismatches
  - Invalid scope access
  - Parameter count mismatches

### 4. Semantic Analysis
- Type checking and validation
- Scope rules enforcement
- Function call validation
- Array bounds checking
- Control flow analysis

## Project Structure
```
compiler_project/
├── src/
│   ├── __init__.py
│   ├── lexer.py          # Lexical analyzer
│   ├── parser.py         # Syntax analyzer
│   ├── semantic.py       # Semantic analyzer
│   ├── symbol_table.py   # Symbol table implementation
│   └── main.py          # Compiler driver
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   └── test_symbol_table.py
├── examples/
│   ├── valid_programs/
│   └── error_cases/
└── docs/
    ├── grammar.md
    └── api.md
```

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd compiler_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python -m src.main <input_file>
```

### Options
```bash
python -m src.main <input_file> [options]
  --verbose    Display detailed analysis information
  --tokens     Show lexical analysis output
  --ast        Display abstract syntax tree
  --symbols    Show symbol table contents
```

## Components

### Symbol Table Implementation
```python
# Example symbol table structure
{
    'global': {
        'variables': {
            'x': {'type': 'int', 'line': 1, 'initialized': False},
            'y': {'type': 'float', 'line': 2, 'initialized': True}
        },
        'functions': {
            'main': {
                'return_type': 'void',
                'parameters': [],
                'line': 4
            }
        }
    },
    'main': {
        'variables': {
            'temp': {'type': 'int', 'line': 5, 'initialized': True}
        },
        'parent': 'global'
    }
}
```

### Example Programs

1. **Valid Program with Multiple Scopes**
```c
void main(void) {
    int x;
    float y;
    
    x = 10;
    y = 20.5;
    
    if (x > 5) {
        int temp;  // Local scope
        temp = x * 2;
    }
    
    while (x > 0) {
        x = x - 1;
        y = y + 1.0;
    }
}
```

2. **Function Declarations and Calls**
```c
int calculate(int a, float b) {
    float result;
    result = a * b;
    return (int)result;
}

void main(void) {
    int x;
    float y;
    int result;
    
    x = 5;
    y = 2.5;
    result = calculate(x, y);
}
```

## Error Handling

### 1. Lexical Errors
- Invalid characters
- Malformed numbers
- Unterminated strings

### 2. Syntax Errors
- Missing semicolons
- Unmatched braces
- Invalid expression structure

### 3. Semantic Errors
- Type mismatches
- Undefined variables
- Invalid function calls
- Array bounds violations

### 4. Symbol Table Errors
- Duplicate declarations
- Undefined references
- Invalid scope access
- Parameter mismatch

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PLY (Python Lex-Yacc) for lexing and parsing
- Contributors and testers
- Academic references and resources

## Team Members and Contributions

### Core Development Team

1. **Gaurav Tiwari**
   - Component: Lexical Analysis (Scanner)
   - Contributions:
     - Implementation of lexical analyzer
     - Token recognition and classification
     - Error detection in lexical phase
     - Scanner optimization and testing

2. **Rishabh Joshi**
   - Component: Syntax Analysis (Parser)
   - Contributions:
     - Parser implementation
     - Grammar rules development
     - Syntax error handling
     - AST (Abstract Syntax Tree) generation

3. **Vaishnavi Durgapal**
   - Component: Semantic Analysis
   - Contributions:
     - Type checking system
     - Scope analysis
     - Control flow validation
     - Semantic error detection

4. **Luv Tiwari**
   - Component: Symbol Table
   - Contributions:
     - Symbol table design and implementation
     - Scope management
     - Symbol tracking and validation
     - Memory management optimization
