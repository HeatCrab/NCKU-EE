/*
 * main.cpp
 * Test program for List class operations.
 * Demonstrates constructors, operators, and stream I/O.
 */

#include "List.h"
#include <iostream>
#include <fstream>
using namespace std;

int main(int argc, char *argv[]) {
    if (argc < 2) {
        cout << "Usage: " << argv[0] << " <input_file>" << endl;
        return 1;
    }

    // Open input file
    ifstream inputFile(argv[1]);
    if (!inputFile) {
        cout << "Error: Cannot open input file " 
             << argv[1] << endl;
        return 1;
    }

    // Open output file
    ofstream outputFile("RESULT");
    if (!outputFile) {
        cout << "Error: Cannot create output file RESULT" 
             << endl;
        return 1;
    }

    // Read the input file into list1 using operator>>
    List list1;
    inputFile >> list1;
    inputFile.close();

    outputFile << "=== Original List (list1) read from "
               << "input file ===" << endl;
    outputFile << list1 << endl;

    // Copy list1 to list2, list3, list4 using 3 different ways
    
    // Way 1: Copy constructor
    List list2(list1);
    outputFile << "=== List2 created using copy constructor ==="
               << endl;
    outputFile << list2 << endl;

    // Way 2: Assignment operator
    List list3;
    list3 = list1;
    outputFile << "=== List3 created using assignment "
               << "operator ===" << endl;
    outputFile << list3 << endl;

    // Way 3: Constructor with assignment
    List list4 = list1;
    outputFile << "=== List4 created using constructor with "
               << "assignment ===" << endl;
    outputFile << list4 << endl;

    // Add two Lists using operator+
    List list5 = list1 + list2;
    outputFile << "=== List5 = list1 + list2 (operator+) ==="
               << endl;
    outputFile << list5 << endl;

    // Use operator++ to add 1 to a List (prefix)
    ++list1;
    outputFile << "=== List1 after prefix increment "
               << "(++list1) ===" << endl;
    outputFile << list1 << endl;

    // Use operator++(long) to add 1 to a List (postfix)
    list2++;
    outputFile << "=== List2 after postfix increment "
               << "(list2++) ===" << endl;
    outputFile << list2 << endl;

    // Use operator+= to add another List to a List
    list3 += list4;
    outputFile << "=== List3 after += list4 (operator+=) ==="
               << endl;
    outputFile << list3 << endl;

    // Use operator-- to subtract 1 from all elements (prefix)
    --list1;
    outputFile << "=== List1 after prefix decrement "
               << "(--list1) ===" << endl;
    outputFile << list1 << endl;

    // Use operator--(long) to subtract 1 from all elements
    // (postfix)
    list2--;
    outputFile << "=== List2 after postfix decrement "
               << "(list2--) ===" << endl;
    outputFile << list2 << endl;

    // === Error Handling Tests ===
    outputFile << "\n=== Error Handling Tests ===" << endl;

    // Test 1: Try to set length when it's already non-zero
    outputFile << "\n--- Test 1: setLength() with non-zero "
               << "length ---" << endl;
    outputFile << "Current list1 length: " << list1.getLength()
               << endl;
    int result = list1.setLength(10);
    outputFile << "Attempting to set length to 10..." << endl;
    outputFile << "Return value: " << result
               << " (0 = error, 1 = success)" << endl;

    // Test 2: Try to access out-of-bounds element with setElement()
    outputFile << "\n--- Test 2: setElement() out of bounds ---"
               << endl;
    unsigned int len = list1.getLength();
    outputFile << "List1 length: " << len << endl;
    outputFile << "Attempting to set element at position "
               << len << "..." << endl;
    result = list1.setElement(len, 999);
    outputFile << "Return value: " << result
               << " (0 = error, 1 = success)" << endl;

    outputFile << "Attempting to set element at position "
               << (len + 5) << "..." << endl;
    result = list1.setElement(len + 5, 999);
    outputFile << "Return value: " << result
               << " (0 = error, 1 = success)" << endl;

    // Test 3: Try to access out-of-bounds element with getElement()
    outputFile << "\n--- Test 3: getElement() out of bounds ---"
               << endl;
    outputFile << "List1 length: " << len << endl;
    outputFile << "Attempting to get element at position "
               << len << "..." << endl;
    long value = list1.getElement(len);
    outputFile << "Return value: " << value
               << " (-99999 = error)" << endl;

    outputFile << "Attempting to get element at position "
               << (len + 10) << "..." << endl;
    value = list1.getElement(len + 10);
    outputFile << "Return value: " << value
               << " (-99999 = error)" << endl;

    // Test 4: Verify getLength() works correctly
    outputFile << "\n--- Test 4: getLength() verification ---"
               << endl;
    outputFile << "list1 length: " << list1.getLength() << endl;
    outputFile << "list2 length: " << list2.getLength() << endl;
    outputFile << "list3 length: " << list3.getLength() << endl;

    outputFile.close();
    cout << "All operations completed. Results written to "
         << "RESULT file." << endl;

    return 0;
}