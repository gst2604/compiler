from ply import yacc
from .lexer import Lexer
from .symbol_table import SymbolTable

class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)
        self.symbol_table = SymbolTable()
        self.ast = None
        self.errors = []
        self.current_line = 1
        self.brace_stack = []  

    def update_line_number(self, p):
        """Update current line number based on token."""
        if p and hasattr(p, 'lineno'):
            self.current_line = p.lineno

    def check_braces(self, data):
        """Check if braces are properly matched in the code."""
        self.brace_stack = []
        lines = data.split('\n')
        for line_num, line in enumerate(lines, 1):
            for char_pos, char in enumerate(line, 1):
                if char in '{(':
                    self.brace_stack.append((char, line_num, char_pos))
                elif char in '})':
                    if not self.brace_stack:
                        self.errors.append(f"Error at line {line_num}, position {char_pos}: Unmatched closing brace '{char}'")
                        return False
                    opening_brace, open_line, open_pos = self.brace_stack.pop()
                    if (opening_brace == '{' and char != '}') or (opening_brace == '(' and char != ')'):
                        self.errors.append(f"Error at line {line_num}, position {char_pos}: Mismatched braces. Found '{char}' but expected matching '{opening_brace}' from line {open_line}, position {open_pos}")
                        return False
        
        if self.brace_stack:
            for brace, line_num, pos in self.brace_stack:
                self.errors.append(f"Error: Unclosed '{brace}' from line {line_num}, position {pos}")
            return False
        return True

    # Program structure
    def p_program(self, p):
        '''program : declaration_list'''
        p[0] = ('program', p[1])
        self.ast = p[0]

    def p_declaration_list(self, p):
        '''declaration_list : declaration_list declaration
                          | declaration'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_declaration(self, p):
        '''declaration : var_declaration
                      | fun_declaration'''
        p[0] = p[1]

    # Variable declarations
    def p_var_declaration(self, p):
        '''var_declaration : type_specifier ID SEMICOLON
                         | type_specifier ID LBRACKET NUMBER RBRACKET SEMICOLON'''
        try:
            if len(p) == 4:
                p[0] = ('var_decl', p[1], p[2])
                # Add variable to current scope
                self.symbol_table.insert(p[2], p[1], p.lineno(2), 'variable')
            else:
                p[0] = ('array_decl', p[1], p[2], p[4])
                # Add array to current scope
                self.symbol_table.insert(p[2], f'array_{p[1]}', p.lineno(2), 'array', size=p[4])
        except Exception as e:
            self.errors.append(f"Error at line {p.lineno(2)}: {str(e)}")

    def p_type_specifier(self, p):
        '''type_specifier : INT
                        | FLOAT
                        | VOID
                        | CHAR
                        | BOOLEAN'''
        p[0] = p[1]

    # Error handling for missing semicolon
    def p_var_declaration_error(self, p):
        '''var_declaration : type_specifier ID error'''
        self.errors.append(f"Error at line {p.lineno(2)}: Missing semicolon after variable declaration")
        p[0] = ('var_decl_error', p[1], p[2])

    # Function declarations
    def p_fun_declaration(self, p):
        '''fun_declaration : type_specifier ID LPAREN params RPAREN compound_stmt'''
        try:
            p[0] = ('fun_decl', p[1], p[2], p[4], p[6])
            self.symbol_table.insert(p[2], f'function_{p[1]}', p.lineno(2))
        except Exception as e:
            self.errors.append(f"Error at line {p.lineno(2)}: {str(e)}")

    def p_params(self, p):
        '''params : param_list
                 | VOID'''
        p[0] = p[1]

    def p_param_list(self, p):
        '''param_list : param_list COMMA param
                     | param'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_param(self, p):
        '''param : type_specifier ID
                | type_specifier ID LBRACKET RBRACKET'''
        if len(p) == 3:
            p[0] = ('param', p[1], p[2])
        else:
            p[0] = ('array_param', p[1], p[2])

    # Statements
    def p_compound_stmt(self, p):
        '''compound_stmt : LBRACE local_declarations statement_list RBRACE'''
        p[0] = ('compound_stmt', p[2], p[3])
        # Enter a new scope for the compound statement
        self.symbol_table.enter_scope('block')

    def p_local_declarations(self, p):
        '''local_declarations : local_declarations var_declaration
                            | empty'''
        if len(p) == 3:
            if p[1]:  # If there are previous declarations
                p[0] = p[1] + [p[2]]
            else:
                p[0] = [p[2]]
        else:
            p[0] = []

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                        | empty'''
        if len(p) == 3:
            if p[1]:  # If there are previous statements
                p[0] = p[1] + [p[2]]
            else:
                p[0] = [p[2]]
        else:
            p[0] = []

    def p_statement(self, p):
        '''statement : expression_stmt
                    | compound_stmt
                    | selection_stmt
                    | iteration_stmt
                    | return_stmt'''
        p[0] = p[1]

    def p_expression_stmt(self, p):
        '''expression_stmt : expression SEMICOLON
                         | SEMICOLON'''
        if len(p) == 3:
            p[0] = ('expr_stmt', p[1])
        else:
            p[0] = ('empty_stmt',)

    # Error handling for missing semicolon in expression
    def p_expression_stmt_error(self, p):
        '''expression_stmt : expression error'''
        self.errors.append(f"Error at line {self.current_line}: Missing semicolon after expression")
        p[0] = ('expr_stmt_error', p[1])

    def p_selection_stmt(self, p):
        '''selection_stmt : IF LPAREN expression RPAREN statement
                        | IF LPAREN expression RPAREN statement ELSE statement'''
        if len(p) == 6:
            p[0] = ('if_stmt', p[3], p[5])
        else:
            p[0] = ('if_else_stmt', p[3], p[5], p[7])

    def p_iteration_stmt(self, p):
        '''iteration_stmt : WHILE LPAREN expression RPAREN statement'''
        p[0] = ('while_stmt', p[3], p[5])

    def p_return_stmt(self, p):
        '''return_stmt : RETURN SEMICOLON
                      | RETURN expression SEMICOLON'''
        if len(p) == 3:
            p[0] = ('return_stmt', None)
        else:
            p[0] = ('return_stmt', p[2])

    # Error handling for missing semicolon in return statement
    def p_return_stmt_error(self, p):
        '''return_stmt : RETURN expression error'''
        self.errors.append(f"Error at line {self.current_line}: Missing semicolon after return statement")
        p[0] = ('return_stmt_error', p[2])

    # Expressions
    def p_expression(self, p):
        '''expression : var ASSIGN expression
                     | logical_expression'''
        if len(p) == 4:
            p[0] = ('assign', p[1], p[3])
        else:
            p[0] = p[1]

    def p_var(self, p):
        '''var : ID
              | ID LBRACKET expression RBRACKET'''
        if len(p) == 2:
            p[0] = ('var', p[1])
        else:
            p[0] = ('array_access', p[1], p[3])

    def p_logical_expression(self, p):
        '''logical_expression : logical_expression OR and_expression
                            | and_expression'''
        if len(p) == 4:
            p[0] = ('or', p[1], p[3])
        else:
            p[0] = p[1]

    def p_and_expression(self, p):
        '''and_expression : and_expression AND simple_expression
                        | simple_expression'''
        if len(p) == 4:
            p[0] = ('and', p[1], p[3])
        else:
            p[0] = p[1]

    def p_simple_expression(self, p):
        '''simple_expression : additive_expression relop additive_expression
                           | additive_expression'''
        if len(p) == 4:
            p[0] = ('relop', p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_relop(self, p):
        '''relop : LE
                | LT
                | GT
                | GE
                | EQ
                | NE'''
        p[0] = p[1]

    def p_additive_expression(self, p):
        '''additive_expression : additive_expression addop term
                             | term'''
        if len(p) == 4:
            p[0] = ('addop', p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_addop(self, p):
        '''addop : PLUS
                | MINUS'''
        p[0] = p[1]

    def p_term(self, p):
        '''term : term mulop factor
                | factor'''
        if len(p) == 4:
            p[0] = ('mulop', p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_mulop(self, p):
        '''mulop : TIMES
                | DIVIDE'''
        p[0] = p[1]

    def p_factor(self, p):
        '''factor : LPAREN expression RPAREN
                 | var
                 | call
                 | NUMBER
                 | FLOAT_NUM
                 | CHAR_LITERAL
                 | TRUE
                 | FALSE'''
        if len(p) == 4:
            p[0] = p[2]
        else:
            if isinstance(p[1], (int, float)):
                p[0] = ('number', p[1])
            elif p[1] == 'true' or p[1] == 'false':
                p[0] = ('boolean', p[1])
            elif isinstance(p[1], str) and len(p[1]) == 1:
                p[0] = ('char', p[1])
            else:
                p[0] = p[1]

    def p_call(self, p):
        '''call : ID LPAREN args RPAREN'''
        p[0] = ('call', p[1], p[3])

    def p_args(self, p):
        '''args : arg_list
               | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_arg_list(self, p):
        '''arg_list : arg_list COMMA expression
                   | expression'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_empty(self, p):
        'empty :'
        pass

    def p_error(self, p):
        if p:
            self.errors.append(f"Syntax error at line {p.lineno}, position {p.lexpos}: Unexpected token '{p.value}'")
        else:
            self.errors.append("Syntax error at EOF")

    def parse(self, data):
        self.errors = []  # Reset errors before parsing
        self.lexer.input(data)
        
        # Check braces before parsing
        if not self.check_braces(data):
            return None
            
        return self.parser.parse(data) 
