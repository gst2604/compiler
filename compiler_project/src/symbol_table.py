class Symbol:
    def __init__(self, name, type, line_no=None, kind='variable', size=None):
        self.name = name
        self.type = type
        self.line_no = line_no
        self.kind = kind
        self.size = size  # For arrays
        self.attributes = {
            'size': None,          # Size for arrays
            'params': [],          # Parameter list for functions
            'return_type': None,   # Return type for functions
            'is_initialized': False,# Whether variable has been initialized
            'memory_location': None,# Symbolic memory location
            'array_dimensions': [], # Dimensions for array types
            'value': None,         # For constant values
            'references': [],      # List of line numbers where symbol is referenced
            'is_constant': False,  # Whether the symbol is a constant
            'access_modifier': 'public'  # Access modifier (public/private)
        }

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.current_scope = 'global'
        self.scope_stack = ['global']
        self.scope_level = 0
        self.next_memory_location = 0
        self.scope_symbols = {"global": set()}
        self.scope_sizes = {"global": 0}

    def enter_scope(self, scope_name):
        """Enter a new scope."""
        # Create a unique scope name by combining parent scope and scope name with a counter
        scope_counter = len([s for s in self.scope_symbols.keys() if s.startswith(f"{self.current_scope}.{scope_name}")])
        qualified_scope = f"{self.current_scope}.{scope_name}_{scope_counter}"
        
        self.scope_stack.append(qualified_scope)
        self.current_scope = qualified_scope
        self.scope_level += 1
        
        # Initialize the new scope's data structures
        if qualified_scope not in self.scope_symbols:
            self.scope_symbols[qualified_scope] = set()
        if qualified_scope not in self.scope_sizes:
            self.scope_sizes[qualified_scope] = 0

    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scope_stack) > 1:
            old_scope = self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
            self.scope_level -= 1
            return old_scope
        return None

    def insert(self, name, type, line_no=None, kind='variable', size=None):
        """Insert a symbol into the current scope."""
        key = (name, self.current_scope)
        
        # For block scopes, allow shadowing of outer scope variables
        if self.current_scope != 'global' and 'block' in self.current_scope:
            # This is fine, we allow shadowing in block scopes
            pass
        # For function parameters and global scope, don't allow redeclaration
        elif key in self.symbols:
            raise Exception(f"Symbol '{name}' already declared in current scope")
            
        self.symbols[key] = Symbol(name, type, line_no, kind, size)
        self.symbols[key].attributes['memory_location'] = self._allocate_memory(type)
        
        # Add to current scope's symbol set
        self.scope_symbols[self.current_scope].add(name)
        
        # Update scope size
        size = self._get_type_size(type)
        self.scope_sizes[self.current_scope] += size
        
        return True

    def lookup(self, name, current_scope_only=False):
        """Look up a symbol in the current and enclosing scopes."""
        if current_scope_only:
            key = (name, self.current_scope)
            if key in self.symbols:
                return self.symbols[key]
            return None
            
        # First try current scope
        key = (name, self.current_scope)
        if key in self.symbols:
            return self.symbols[key]
        
        # Then try enclosing scopes
        for scope in reversed(self.scope_stack[:-1]):
            key = (name, scope)
            if key in self.symbols:
                return self.symbols[key]
        return None

    def update_symbol(self, name, **attributes):
        """Update symbol attributes."""
        symbol = self.lookup(name)
        if symbol:
            for key, value in attributes.items():
                if key == 'is_initialized' and value:
                    symbol.attributes['is_initialized'] = True
                elif key == 'params' and symbol.kind == 'function':
                    symbol.attributes['params'] = value
                elif key == 'size' and symbol.kind == 'array':
                    symbol.attributes['size'] = value
                    symbol.attributes['array_dimensions'] = [value]
                else:
                    symbol.attributes[key] = value
            return True
        return False

    def get_symbols_in_scope(self, scope=None):
        """Get all symbols in a specific scope."""
        if scope is None:
            scope = self.current_scope
        
        if scope not in self.scope_symbols:
            return {}
        
        return {
            name: self.symbols.get((name, scope))
            for name in self.scope_symbols[scope]
        }

    def get_all_references(self, name):
        """Get all references to a symbol."""
        symbol = self.lookup(name)
        if symbol:
            return symbol.attributes['references']
        return []

    def _allocate_memory(self, type):
        """Allocate symbolic memory location."""
        location = self.next_memory_location
        size = self._get_type_size(type)
        self.next_memory_location += size
        return location

    def _get_type_size(self, type):
        """Get size of a type in symbolic memory units."""
        if type is None:
            return 0
        type_sizes = {
            'int': 4,
            'float': 4,
            'char': 1,
            'boolean': 1,
            'void': 0
        }
        base_type = type.split('_')[0] if '_' in type else type
        return type_sizes.get(base_type, 4)  # Default to 4 for unknown types

    def _add_reference(self, symbol, line_number):
        """Add a reference to a symbol."""
        if line_number and line_number not in symbol.attributes['references']:
            symbol.attributes['references'].append(line_number)

    def _get_current_line(self):
        """Get current line number from the parser/lexer."""
        return None

    def get_scope_size(self, scope=None):
        """Get the total memory size needed for a scope."""
        if scope is None:
            scope = self.current_scope
        return self.scope_sizes.get(scope, 0)

    def get_scope_level(self):
        """Get current scope nesting level."""
        return self.scope_level

    def is_global_scope(self):
        """Check if current scope is global."""
        return self.current_scope == "global"

    def get_function_parameters(self, function_name):
        """Get parameters of a function."""
        symbol = self.lookup(function_name)
        if symbol and symbol.kind == 'function':
            return symbol.attributes['params']
        return []

    def get_symbol_info(self, name):
        """Get detailed information about a symbol."""
        symbol = self.lookup(name)
        if not symbol:
            return None
        
        return {
            'name': symbol.name,
            'type': symbol.type,
            'kind': symbol.kind,
            'scope': symbol.scope,
            'line_declared': symbol.line_no,
            'memory_location': symbol.attributes['memory_location'],
            'is_initialized': symbol.attributes['is_initialized'],
            'references': symbol.attributes['references'],
            'size': symbol.attributes['size'],
            'attributes': symbol.attributes
        }