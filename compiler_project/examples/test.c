// Example program
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
} 