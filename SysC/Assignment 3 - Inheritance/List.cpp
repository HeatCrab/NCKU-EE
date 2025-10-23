/*
 * List.cpp
 * Implementation of the List class.
 */

#include "List.h"
#include <iostream>
using namespace std;

/*
 * Default constructor.
 * Initializes an empty list with length 0.
 */
List::List() : Node() {
    length = 0;
}

/*
 * Constructor with specified length.
 * Creates a list with given length and allocates memory.
 */
List::List(unsigned int _length) : Node(_length) {
    length = _length;
}

/*
 * Copy constructor.
 * Creates a deep copy of another list.
 */
List::List(const List &other) : Node(other.length) {
    length = other.length;
    for (unsigned int i = 0; i < length; i++) {
        _Node[i] = other._Node[i];
    }
}

/*
 * Destructor.
 * Cleans up and resets length to 0.
 */
List::~List() {
    length = 0;
}

/*
 * Assignment operator.
 * Performs deep copy from another list.
 */
List& List::operator=(const List& other) {
    if (this != &other) {
        reCreate(other.length);
        length = other.length;
        for (unsigned int i = 0; i < length; i++) {
            _Node[i] = other._Node[i];
        }
    }
    return *this;
}

/*
 * Sets the length of the list.
 * Can only be set once when length is 0.
 */
int List::setLength(unsigned int _length) {
    if (length == 0) {
        length = _length;
        reCreate(length);
        return 1;
    } else {
        cout << "Error: Length is already set to " 
             << length << endl;
        return 0;
    }
}

/*
 * Returns the current length of the list.
 */
unsigned int List::getLength() {
    return length;
}

/*
 * Sets the value of an element at specified position.
 * Returns 1 on success, 0 if position is out of bounds.
 */
int List::setElement(unsigned int pos, long val) {
    if (pos < length) {
        _Node[pos] = val;
        return 1;
    } else {
        cout << "Error: Position " << pos 
             << " is out of bounds" << endl;
        return 0;
    }
}

/*
 * Gets the value of an element at specified position.
 * Returns -99999 if position is out of bounds.
 */
long List::getElement(unsigned int pos) {
    if (pos < length) {
        return _Node[pos];
    } else {
        cout << "Error: Position " << pos 
             << " is out of bounds" << endl;
        return -99999;
    }
}

/*
 * Addition operator.
 * Adds corresponding elements of two lists.
 */
List List::operator+(const List &other) {
    List result(length);
    for (unsigned int i = 0; i < length; i++) {
        result._Node[i] = _Node[i] 
                          + (i < other.length ? other._Node[i] : 0);
    }
    return result;
}

/*
 * Addition assignment operator.
 * Adds another list to this list element-wise.
 */
List& List::operator+=(const List &other) {
    for (unsigned int i = 0; i < length && i < other.length; i++) {
        _Node[i] += other._Node[i];
    }
    return *this;
}

/*
 * Prefix increment operator.
 * Increments all elements by 1.
 */
List List::operator++() {
    for (unsigned int i = 0; i < length; i++) {
        ++_Node[i];
    }
    return *this;
}

/*
 * Postfix increment operator.
 * Increments all elements by 1, returns old value.
 */
List List::operator++(int) {
    List temp(*this);
    for (unsigned int i = 0; i < length; i++) {
        _Node[i]++;
    }
    return temp;
}

/*
 * Prefix decrement operator.
 * Decrements all elements by 1.
 */
List List::operator--() {
    for (unsigned int i = 0; i < length; i++) {
        --_Node[i];
    }
    return *this;
}

/*
 * Postfix decrement operator.
 * Decrements all elements by 1, returns old value.
 */
List List::operator--(int) {
    List temp(*this);
    for (unsigned int i = 0; i < length; i++) {
        _Node[i]--;
    }
    return temp;
}

/*
 * Stream output operator.
 * Prints list length and all elements.
 */
ostream& operator<<(ostream &out, List list) {
    out << "List length: " << list.length << endl;
    out << "Elements: ";
    for (unsigned int i = 0; i < list.length; i++) {
        out << list._Node[i];
        if (i < list.length - 1) {
            out << " ";
        }
    }
    out << endl;
    return out;
}

/*
 * Stream input operator.
 * Reads list length and elements from input stream.
 */
istream& operator>>(istream &in, List &list) {
    unsigned int len;
    in >> len;
    list.setLength(len);
    for (unsigned int i = 0; i < len; i++) {
        long val;
        in >> val;
        list.setElement(i, val);
    }
    return in;
}