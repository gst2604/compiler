// Test program for semantic analysis
int add(int a, int b) {
    return a + b;  // Type check: int + int = int
}

void main(void) {
    int x;
    float y;
    boolean flag;
    int numbers[5];
    char c;

    // Type mismatch in assignment
    x = 42.5;      // Error: assigning float to int

    // Undefined variable
    z = 10;        // Error: z is not declared

    // Type mismatch in operation
    y = x + flag;  // Error: cannot add int and boolean

    // Array index type check
    numbers[flag]; // Error: array index must be integer
    numbers[1.5];  // Error: array index must be integer

    // Function call parameter mismatch
    add(x, y);     // Error: second parameter should be int, not float
    add(x);        // Error: wrong number of arguments

    // Type mismatch in conditions
    if (x + y) {   // Error: condition must be boolean
        x = 1;
    }

    // Invalid operation on types
    c = x + c;     // Error: cannot add int and char

    // Correct operations
    x = 10;        // OK: int assignment
    y = 20.5;      // OK: float assignment
    flag = true;   // OK: boolean assignment
    numbers[0] = 1;// OK: array assignment with int index
    
    if (flag && x > 5) { // OK: boolean condition
        x = add(x, 2);   // OK: correct function call
    }
} 