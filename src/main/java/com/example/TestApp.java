package com.example;

public class TestApp {
    private static int unusedField; // SpotBugs: Unused field
    private static String unusedString; //unused field

    public static void main(String[] args) {
        TestApp app = new TestApp();
        app.doSomething(null); // SpotBugs: Possible null dereference
        System.out.println("Hello, World!"); // Checkstyle: Magic string, print statement
    }

    // Missing Javadoc (Checkstyle)
    public void doSomething(String value) {
        if (value.equals("test")) { // SpotBugs: Possible NPE
            System.out.println("Value is test"); // Checkstyle: Magic string
        }
    }

    private int addNumbers(int a, int b) { // Missing Javadoc (Checkstyle)
        int result = a + b; // Unused assignment (SpotBugs)
        return a + b; // Redundant computation
    }

    public boolean badEquals(Object obj) { // SpotBugs: Bad equals
        return false; // Dummy implementation
    }

    public int hashCode() { // SpotBugs: Bad hashCode
        return 42; // Magic number, bad hash
    }

}
