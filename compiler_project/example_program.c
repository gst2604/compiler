// Simple grade calculator
void main(void) {
    int score;
    char grade;
    float average;
    boolean passed;

    // Initialize score
    score = 85;

    // Determine grade
    if (score >= 90) {
        grade = 'A';
    } else if (score >= 80) {
        grade = 'B';
    } else if (score >= 70) {
        grade = 'C';
    } else if (score >= 60) {
        grade = 'D';
    } else {
        grade = 'F';
    }

    // Check if passed
    if (score >= 60) {
        passed = true;
    } else {
        passed = false;
    }
} 