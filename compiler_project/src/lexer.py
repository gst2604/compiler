from ply import lex

class Lexer:
    def __init__(self):
        self.last_token = None
        self.lexer = lex.lex(module=self)

    # Reserved words
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'int': 'INT',
        'float': 'FLOAT',
        'void': 'VOID',
        'char': 'CHAR',
        'boolean': 'BOOLEAN',
        'true': 'TRUE',
        'false': 'FALSE'
    }

    # Token list
    tokens = [
        'ID', 'NUMBER', 'FLOAT_NUM', 'CHAR_LITERAL',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        'AND', 'OR',  # Logical operators
        'ASSIGN',
        'SEMICOLON', 'COMMA',
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',  # For compound statements
        'LBRACKET', 'RBRACKET',  # For array indices
        'TRUE', 'FALSE'
    ] + list(reserved.values())

    # Simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_ASSIGN = r'='
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'  # For compound statements
    t_RBRACE = r'\}'  # For compound statements
    t_LBRACKET = r'\['  # For array indices
    t_RBRACKET = r'\]'  # For array indices

    # Complex tokens
    def t_FLOAT_NUM(self, t):
        r'\d*\.\d+'
        t.value = float(t.value)
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_CHAR_LITERAL(self, t):
        r'\'.\''
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_ID(self, t):
        r'[A-Za-z][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    # Comments
    def t_COMMENT(self, t):
        r'//.*'
        pass

    # Whitespace
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    # Error handling
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    # Input handling
    def input(self, data):
        self.lexer.input(data)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def test(self, data):
        self.input(data)
        while True:
            tok = self.token()
            if not tok:
                break
            print(tok) 