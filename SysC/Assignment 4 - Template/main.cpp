#include "List.h"
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(int argc, char *argv[]) {
    /*
     * Verify command line arguments.
     * argc should be 3: program name, double file, string file.
     */
    if (argc != 3) {
        cout << "Usage: " << argv[0] 
             << " <double_file> <string_file>" << endl;
        return 1;
    }

    /* Open double input file */
    ifstream doubleFile(argv[1]);
    if (!doubleFile) {
        cout << "Error: Cannot open double file " 
             << argv[1] << endl;
        return 1;
    }

    /* Open string input file */
    ifstream stringFile(argv[2]);
    if (!stringFile) {
        cout << "Error: Cannot open string file " 
             << argv[2] << endl;
        return 1;
    }

    /* Read double data and construct List<double> */
    unsigned int doubleLength;
    doubleFile >> doubleLength;
    
    List<double> doubleList1(doubleLength);
    for (unsigned int i = 0; i < doubleLength; i++) {
        double val;
        doubleFile >> val;
        doubleList1.setElement(i, val);
    }
    doubleFile.close();

    /* Read string data and construct List<string> */
    unsigned int stringLength;
    stringFile >> stringLength;
    
    List<string> stringList1(stringLength);
    for (unsigned int i = 0; i < stringLength; i++) {
        string val;
        stringFile >> val;
        stringList1.setElement(i, val);
    }
    stringFile.close();

    /* Display original lists */
    cout << "=== Original double list (doubleList1) ===" << endl;
    cout << doubleList1 << endl;

    cout << "=== Original string list (stringList1) ===" << endl;
    cout << stringList1 << endl;

    /*
     * Use copy constructor to create second double list.
     */
    List<double> doubleList2(doubleList1);
    cout << "=== Double list 2 created using copy constructor ==="
         << endl;
    cout << doubleList2 << endl;

    /*
     * Use assignment operator to create second string list.
     */
    List<string> stringList2;
    stringList2 = stringList1;
    cout << "=== String list 2 created using assignment operator ==="
         << endl;
    cout << stringList2 << endl;

    /*
     * Use operator== to check if the lists are the same.
     */
    if (doubleList1 == doubleList2) {
        cout << "Comparison result: doubleList1 == doubleList2 "
             << "(TRUE)" << endl << endl;
    } else {
        cout << "Comparison result: doubleList1 != doubleList2 "
             << "(FALSE)" << endl << endl;
    }

    if (stringList1 == stringList2) {
        cout << "Comparison result: stringList1 == stringList2 "
             << "(TRUE)" << endl << endl;
    } else {
        cout << "Comparison result: stringList1 != stringList2 "
             << "(FALSE)" << endl << endl;
    }

    /*
     * Modify lists using setElement() to demonstrate changes.
     */
    cout << "=== Modifying doubleList1 using setElement() ===" 
         << endl;
    for (unsigned int i = 0; i < doubleList1.getLength(); i++) {
        doubleList1.setElement(i, doubleList1.getElement(i) + 1.0);
    }
    cout << doubleList1 << endl;

    cout << "=== Modifying stringList1 using setElement() ===" 
         << endl;
    for (unsigned int i = 0; i < stringList1.getLength(); i++) {
        stringList1.setElement(i, 
                               stringList1.getElement(i) + "_modified");
    }
    cout << stringList1 << endl;

    /*
     * Verify that the copies remain unchanged.
     */
    cout << "=== Verify doubleList2 remains unchanged ===" << endl;
    cout << doubleList2 << endl;

    cout << "=== Verify stringList2 remains unchanged ===" << endl;
    cout << stringList2 << endl;

    /*
     * Error handling tests to ensure complete coverage.
     */
    cout << "\n=== Error Handling Tests ===" << endl;

    cout << "\n--- Test 1: setLength() with non-zero length ---"
         << endl;
    cout << "Current doubleList1 length: "
         << doubleList1.getLength() << endl;
    cout << "Attempting to set length to 10..." << endl;
    int result = doubleList1.setLength(10);
    cout << "Return value: " << result
         << " (0 = error, 1 = success)" << endl << endl;

    cout << "--- Test 2: setElement() out of bounds ---" << endl;
    unsigned int len = doubleList1.getLength();
    cout << "doubleList1 length: " << len << endl;
    cout << "Attempting to set element at position " << len
         << "..." << endl;
    result = doubleList1.setElement(len, 999.99);
    cout << "Return value: " << result
         << " (0 = error, 1 = success)" << endl;

    cout << "Attempting to set element at position " << (len + 5)
         << "..." << endl;
    result = doubleList1.setElement(len + 5, 999.99);
    cout << "Return value: " << result
         << " (0 = error, 1 = success)" << endl << endl;

    cout << "--- Test 3: setElement() out of bounds for string list ---"
         << endl;
    len = stringList1.getLength();
    cout << "stringList1 length: " << len << endl;
    cout << "Attempting to set element at position " << len
         << "..." << endl;
    result = stringList1.setElement(len, "invalid");
    cout << "Return value: " << result
         << " (0 = error, 1 = success)" << endl << endl;

    cout << "--- Test 4: Verify getLength() works correctly ---"
         << endl;
    cout << "doubleList1 length: " << doubleList1.getLength() << endl;
    cout << "doubleList2 length: " << doubleList2.getLength() << endl;
    cout << "stringList1 length: " << stringList1.getLength() << endl;
    cout << "stringList2 length: " << stringList2.getLength()
         << endl << endl;

    cout << "Note: getElement() with out-of-bounds access uses assert "
         << "and will terminate the program," << endl;
    cout << "so it cannot be safely tested in this test suite."
         << endl << endl;

    cout << "All operations completed successfully." << endl;

    return 0;
}