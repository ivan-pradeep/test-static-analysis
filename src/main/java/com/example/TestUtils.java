package com.example;

public class TestUtils {
    // Missing Javadoc (Checkstyle)
    public static int doCalc(int x) {
        if (x == 42) { // Magic number (Checkstyle)
            return x;
        } else if (x == 0) {
            return 1 / x; // SpotBugs: Possible divide by zero
        }
        return x * 2;
    }

    private static String unusedMethod() { // SpotBugs: Unused method
        return "unused";
    }

    // Variable naming (Checkstyle)
    public void fooBar() {
        int BAD_naming = 1; // Bad variable naming
        System.out.println(BAD_naming); // Print statement, magic number
    }
}