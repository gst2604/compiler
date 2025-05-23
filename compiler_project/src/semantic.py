class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self.current_function = None

    def analyze(self, ast):
        """Analyze the AST for semantic correctness."""
        if ast is None:
            return False
        self.visit(ast)
        return len(self.errors) == 0

    def visit(self, node):
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            if hasattr(self, method_name):
                return getattr(self, method_name)(node)
            else:
                return self.visit_children(node)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)
        return None

    def visit_children(self, node):
        for child in node[1:]:
            self.visit(child)

    def visit_program(self, node):
        self.visit(node[1])

    def visit_var_decl(self, node):
        """Handle variable declarations."""
        var_type, var_name = node[1], node[2]
        if not self.is_valid_type(var_type):
            self.errors.append(f"Invalid type '{var_type}' for variable '{var_name}'")
        else:
            # Add variable to current scope
            try:
                self.symbol_table.insert(var_name, var_type, kind='variable')
            except Exception as e:
                self.errors.append(str(e))

    def visit_fun_decl(self, node):
        """Handle function declarations."""
        fun_type, fun_name, params, body = node[1], node[2], node[3], node[4]
        
        # Add function to symbol table
        try:
            self.symbol_table.insert(fun_name, f'function_{fun_type}', kind='function')
        except Exception as e:
            self.errors.append(str(e))
            return
            
        # Enter function scope
        self.current_function = fun_name
        self.symbol_table.enter_scope(fun_name)
        
        # Process parameters if they exist
        param_types = []
        if params != 'void':
            for param in params:
                param_type, param_name = param[1], param[2]
                param_types.append(param_type)
                try:
                    self.symbol_table.insert(param_name, param_type, kind='parameter')
                except Exception as e:
                    self.errors.append(str(e))
        
        # Update function with parameter types
        self.symbol_table.update_symbol(fun_name, params=param_types)
        
        # Process function body
        self.visit(body)
        
        # Exit function scope
        self.symbol_table.exit_scope()
        self.current_function = None

    def visit_compound_stmt(self, node):
        """Handle compound statements."""
        local_decls, stmt_list = node[1], node[2]
        
        # Enter a new block scope
        self.symbol_table.enter_scope('block')
        
        # Process all local declarations
        for decl in local_decls:
            self.visit(decl)
        
        # Process all statements
        for stmt in stmt_list:
            self.visit(stmt)
            
        # Exit the block scope
        self.symbol_table.exit_scope()

    def visit_assign(self, node):
        """Handle assignment statements."""
        var_node, expr = node[1], node[2]
        if isinstance(var_node, tuple) and var_node[0] == 'var':
            var_name = var_node[1]
            var_symbol = self.symbol_table.lookup(var_name)
            
            if not var_symbol:
                self.errors.append(f"Variable '{var_name}' not declared")
            else:
                # Mark variable as initialized
                self.symbol_table.update_symbol(var_name, is_initialized=True)
                
                # Check type compatibility
                expr_type = self.get_expr_type(expr)
                if expr_type and not self.are_types_compatible(var_symbol.type, expr_type):
                    self.errors.append(f"Type mismatch: cannot assign {expr_type} to {var_symbol.type}")

    def visit_if_stmt(self, node):
        """Handle if statements."""
        condition, then_stmt = node[1], node[2]
        self.visit(condition)
        self.visit(then_stmt)

    def visit_if_else_stmt(self, node):
        """Handle if-else statements."""
        condition, then_stmt, else_stmt = node[1], node[2], node[3]
        self.visit(condition)
        self.visit(then_stmt)
        self.visit(else_stmt)

    def visit_while_stmt(self, node):
        """Handle while statements."""
        condition, body = node[1], node[2]
        self.visit(condition)
        self.visit(body)

    def visit_return_stmt(self, node):
        """Handle return statements."""
        if not self.current_function:
            self.errors.append("Return statement outside function")
            return

        expr = node[1]
        fun_type = self.symbol_table.lookup(self.current_function).type.replace('function_', '')
        
        if fun_type == 'void':
            if expr:
                self.errors.append(f"Void function '{self.current_function}' cannot return a value")
            return
            
        if not expr and fun_type != 'void':
            self.errors.append(f"Function '{self.current_function}' must return a value of type {fun_type}")
            return
            
        if expr:
            expr_type = self.get_expr_type(expr)
            if expr_type is None:
                self.errors.append(f"Invalid return expression in function '{self.current_function}'")
            elif not self.are_types_compatible(fun_type, expr_type):
                self.errors.append(f"Return type mismatch: expected {fun_type}, got {expr_type}")

    def get_expr_type(self, node):
        """Get the type of an expression."""
        if isinstance(node, tuple):
            if node[0] == 'number':
                return 'int' if isinstance(node[1], int) else 'float'
            elif node[0] == 'char':
                return 'char'
            elif node[0] == 'boolean':
                return 'boolean'
            elif node[0] == 'var':
                var_symbol = self.symbol_table.lookup(node[1])
                return var_symbol.type if var_symbol else None
            elif node[0] == 'call':
                fun_symbol = self.symbol_table.lookup(node[1])
                return fun_symbol.type.replace('function_', '') if fun_symbol else None
            elif node[0] == 'relop':
                left_type = self.get_expr_type(node[2])
                right_type = self.get_expr_type(node[3])
                if left_type in ('int', 'float') and right_type in ('int', 'float'):
                    return 'boolean'
                else:
                    self.errors.append(f"Invalid operands for comparison: {left_type} and {right_type}")
                    return None
            elif node[0] in ('and', 'or'):
                left_type = self.get_expr_type(node[1])
                right_type = self.get_expr_type(node[2])
                if left_type == 'boolean' and right_type == 'boolean':
                    return 'boolean'
                else:
                    self.errors.append(f"Invalid operands for {node[0]}: {left_type} and {right_type}")
                    return None
            elif node[0] in ('mulop', 'addop'):
                left_type = self.get_expr_type(node[2])
                right_type = self.get_expr_type(node[3])
                if left_type in ('int', 'float') and right_type in ('int', 'float'):
                    return 'float' if 'float' in (left_type, right_type) else 'int'
                else:
                    self.errors.append(f"Invalid operands for {node[1]}: {left_type} and {right_type}")
                    return None
        return None

    def is_valid_type(self, type_name):
        """Check if a type is valid."""
        return type_name in ['int', 'float', 'void', 'char', 'boolean']

    def are_types_compatible(self, type1, type2):
        """Check if two types are compatible for assignment."""
        if type1 == type2:
            return True
        if type1 == 'float' and type2 == 'int':
            return True
        return False

    def visit_call(self, node):
        fun_name = node[1]
        if not self.symbol_table.lookup(fun_name):
            self.errors.append(f"Function '{fun_name}' not declared")
        else:
            # Check argument types
            expected_types = self.get_param_types(fun_name)
            actual_types = [self.get_expr_type(arg) for arg in node[2]]
            
            if len(expected_types) != len(actual_types):
                self.errors.append(f"Wrong number of arguments for function '{fun_name}'")
            else:
                for i, (expected, actual) in enumerate(zip(expected_types, actual_types)):
                    if not self.are_types_compatible(expected, actual):
                        self.errors.append(f"Type mismatch in argument {i+1} of function '{fun_name}': expected {expected}, got {actual}")

    def get_param_types(self, fun_name):
        symbol = self.symbol_table.lookup(fun_name)
        if symbol and 'params' in symbol.attributes:
            return symbol.attributes['params']
        return []

    def _analyze_declarations(self, declarations):
        """Analyze global declarations."""
        for decl in declarations:
            if decl[0] == 'var_decl':
                self._analyze_var_declaration(decl)
            elif decl[0] == 'fun_decl':
                self._analyze_function_declaration(decl)

    def _analyze_var_declaration(self, decl):
        """Analyze variable declaration."""
        _, type_spec, var_name = decl
        if type_spec == 'void':
            self.errors.append(f"Error: Variable '{var_name}' declared void")
        # Add variable to current scope
        self.symbol_table.insert(var_name, type_spec)

    def _analyze_function_declaration(self, decl):
        """Analyze function declaration."""
        _, return_type, name, params, body = decl
        # Add function to global scope
        self.symbol_table.insert(name, f'function_{return_type}')
        
        self.current_function = name
        self.symbol_table.enter_scope(name)

        # Analyze parameters
        if params != 'void':
            for param in params:
                param_type, param_name = param[1:]
                if param_type == 'void':
                    self.errors.append(f"Error: Parameter '{param_name}' cannot be void")
                # Add parameter to function scope
                self.symbol_table.insert(param_name, param_type)

        # Analyze function body
        self._analyze_compound_statement(body)
        
        # Check return type consistency
        if return_type != 'void':
            if not self._has_return_statement(body):
                self.errors.append(f"Error: Function '{name}' must return a value")

        self.symbol_table.exit_scope()
        self.current_function = None

    def _analyze_compound_statement(self, stmt):
        """Analyze compound statement."""
        _, local_decls, stmt_list = stmt
        
        # Analyze local declarations
        for decl in local_decls:
            self._analyze_var_declaration(decl)
        
        # Analyze statements
        for statement in stmt_list:
            self._analyze_statement(statement)

    def _analyze_statement(self, stmt):
        """Analyze a statement."""
        stmt_type = stmt[0]
        
        if stmt_type == 'expr_stmt':
            self._analyze_expression(stmt[1])
        elif stmt_type == 'compound_stmt':
            # Create new scope for compound statement
            self.symbol_table.enter_scope('block')
            self._analyze_compound_statement(stmt)
            self.symbol_table.exit_scope()
        elif stmt_type == 'if_stmt':
            self._analyze_if_statement(stmt)
        elif stmt_type == 'if_else_stmt':
            self._analyze_if_else_statement(stmt)
        elif stmt_type == 'while_stmt':
            self._analyze_while_statement(stmt)
        elif stmt_type == 'return_stmt':
            self._analyze_return_statement(stmt)

    def _analyze_if_statement(self, stmt):
        """Analyze if statement."""
        _, condition, body = stmt
        self._analyze_expression(condition)
        self._analyze_statement(body)

    def _analyze_if_else_statement(self, stmt):
        """Analyze if-else statement."""
        _, condition, if_body, else_body = stmt
        self._analyze_expression(condition)
        self._analyze_statement(if_body)
        self._analyze_statement(else_body)

    def _analyze_while_statement(self, stmt):
        """Analyze while statement."""
        _, condition, body = stmt
        self._analyze_expression(condition)
        self._analyze_statement(body)

    def _analyze_return_statement(self, stmt):
        """Analyze return statement."""
        if not self.current_function:
            self.errors.append("Error: Return statement outside function")
            return

        _, expr = stmt
        if expr:
            expr_type = self._analyze_expression(expr)
            func_type = self.symbol_table.lookup(self.current_function).type
            expected_type = func_type.split('_')[1]
            if expr_type != expected_type:
                self.errors.append(f"Error: Return type mismatch in function '{self.current_function}'")

    def _analyze_expression(self, expr):
        """Analyze expression and return its type."""
        if isinstance(expr, tuple):
            if expr[0] == 'number':
                return 'int' if isinstance(expr[1], int) else 'float'
            elif expr[0] == 'var':
                var_symbol = self.symbol_table.lookup(expr[1])
                return var_symbol.type if var_symbol else None
            elif expr[0] == 'array_access':
                return self.visit_array_access(expr)
            elif expr[0] == 'call':
                return self._analyze_function_call(expr)
            elif expr[0] in ('addop', 'mulop'):
                left_type = self._analyze_expression(expr[2])
                right_type = self._analyze_expression(expr[3])
                if left_type == right_type == 'int':
                    return 'int'
                elif left_type in ('int', 'float') and right_type in ('int', 'float'):
                    return 'float'
                else:
                    self.errors.append(f"Invalid operand types for {expr[1]}: {left_type} and {right_type}")
                    return None
            elif expr[0] == 'relop':
                left_type = self._analyze_expression(expr[2])
                right_type = self._analyze_expression(expr[3])
                if left_type in ('int', 'float') and right_type in ('int', 'float'):
                    return 'boolean'
                else:
                    self.errors.append(f"Invalid operand types for comparison: {left_type} and {right_type}")
                    return None
        return None

    def _analyze_var(self, expr):
        """Analyze variable reference."""
        _, var_name = expr
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            self.errors.append(f"Undefined variable '{var_name}'")
            return None
        return symbol.type

    def _analyze_assignment(self, expr):
        """Analyze assignment expression."""
        _, target, value = expr
        target_type = self._analyze_var(target)
        value_type = self._analyze_expression(value)
        
        if target_type and value_type and target_type != value_type:
            self.errors.append(f"Error: Type mismatch in assignment")
        
        return target_type

    def _analyze_function_call(self, expr):
        """Analyze function call."""
        _, func_name, args = expr
        symbol = self.symbol_table.lookup(func_name)
        
        if not symbol:
            self.errors.append(f"Error: Undefined function '{func_name}'")
            return None
            
        if not symbol.type.startswith('function_'):
            self.errors.append(f"Error: '{func_name}' is not a function")
            return None
        
        # Check argument types
        expected_types = symbol.attributes.get('params', [])
        actual_types = [self._analyze_expression(arg) for arg in args]
        
        if len(expected_types) != len(actual_types):
            self.errors.append(f"Error: Wrong number of arguments for function '{func_name}'")
            return None
            
        for i, (expected, actual) in enumerate(zip(expected_types, actual_types)):
            if actual is None:
                return None
            if not self.are_types_compatible(expected, actual):
                self.errors.append(f"Error: Type mismatch in argument {i+1} of function '{func_name}': expected {expected}, got {actual}")
                return None
                
        return symbol.type.split('_')[1]

    def _analyze_binary_operation(self, expr):
        """Analyze binary operation."""
        _, op, left, right = expr
        left_type = self._analyze_expression(left)
        right_type = self._analyze_expression(right)
        
        # If either operand is None, return None
        if not left_type or not right_type:
            return None
            
        # If both operands are numeric (int or float)
        if left_type in ('int', 'float') and right_type in ('int', 'float'):
            # If either is float, result is float
            return 'float' if 'float' in (left_type, right_type) else 'int'
        else:
            self.errors.append(f"Error: Invalid operands for {op}: {left_type} and {right_type}")
            return None

    def _analyze_relational_operation(self, expr):
        """Analyze relational operation."""
        _, op, left, right = expr
        left_type = self._analyze_expression(left)
        right_type = self._analyze_expression(right)
        
        if left_type and right_type and left_type != right_type:
            self.errors.append(f"Error: Type mismatch in relational operation")
        
        return 'int'  # Boolean result

    def _has_return_statement(self, compound_stmt):
        """Check if a compound statement contains a return statement."""
        _, _, stmt_list = compound_stmt
        
        for stmt in stmt_list:
            if stmt[0] == 'return_stmt' and stmt[1] is not None:
                return True
            elif stmt[0] == 'compound_stmt':
                if self._has_return_statement(stmt):
                    return True
            elif stmt[0] in ('if_stmt', 'if_else_stmt'):
                # For if statements, we need all branches to return
                if stmt[0] == 'if_stmt':
                    continue  # Single branch is not enough
                else:
                    if (self._has_return_statement(stmt[2]) and 
                        self._has_return_statement(stmt[3])):
                        return True
        
        return False

    def visit_array_decl(self, node):
        """Handle array declarations."""
        array_type, array_name, size = node[1], node[2], node[3]
        if size <= 0:
            self.errors.append(f"Array size must be positive, got {size}")
            return False
        return True

    def visit_array_access(self, node):
        """Handle array access."""
        array_name, index_expr = node[1], node[2]
        # Check if array exists
        array_symbol = self.symbol_table.lookup(array_name)
        if not array_symbol:
            self.errors.append(f"Undefined array '{array_name}'")
            return None
        if not array_symbol.type.startswith('array_'):
            self.errors.append(f"'{array_name}' is not an array")
            return None
            
        # Check index type
        index_type = self._analyze_expression(index_expr)
        if index_type != 'int':
            self.errors.append(f"Array index must be an integer, got {index_type}")
            return None
            
        # Return the base type of the array (e.g., 'int' from 'array_int')
        return array_symbol.type.replace('array_', '') 