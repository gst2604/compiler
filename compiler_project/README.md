# Simple Compiler Implementation

This project implements a basic compiler with the following components:
- Lexical Analyzer (Scanner)
- Syntax Analyzer (Parser)
- Semantic Analyzer
- Symbol Table

## Project Structure
```
compiler_project/
├── src/
│   ├── lexer.py         # Lexical Analyzer
│   ├── parser.py        # Syntax Analyzer
│   ├── semantic.py      # Semantic Analyzer
│   ├── symbol_table.py  # Symbol Table implementation
│   └── main.py         # Main compiler driver
├── tests/              # Test files
├── examples/           # Example source code files
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the compiler:
```bash
python src/main.py <input_file>
```

## Components

### 1. Lexical Analyzer
- Breaks down source code into tokens
- Handles identifiers, keywords, operators, etc.
- Removes comments and whitespace

### 2. Syntax Analyzer
- Builds parse tree from tokens
- Validates program structure
- Uses grammar rules for the language

### 3. Semantic Analyzer
- Type checking
- Variable declaration checks
- Scope validation

### 4. Symbol Table
- Stores identifiers and their attributes
- Manages scope information
- Supports symbol lookup 