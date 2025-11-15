#ifndef LIST_H
#define LIST_H

#include "Node.h"
#include <iostream>
#include <cassert>
using namespace std;

template <typename T>
class List : public Node<T> {
private:
    unsigned int length;

public:
    /*
     * Default constructor.
     * Calls Node<T>() to initialize _Node.
     * Initializes length as 0.
     */
    List() : Node<T>() {
        length = 0;
    }

    /*
     * Constructor with specified length.
     * Calls Node<T>(_length) to initialize _Node.
     * Initializes length as _length.
     */
    List(unsigned int _length) : Node<T>(_length) {
        length = _length;
    }

    /*
     * Copy constructor.
     * Creates a deep copy of another list.
     */
    List(const List<T> &other) : Node<T>() {
        length = other.length;
        if (other._Node != NULL && length > 0) {
            this->_Node = new T[length];
            for (unsigned int i = 0; i < length; i++) {
                this->_Node[i] = other._Node[i];
            }
        } else {
            this->_Node = NULL;
        }
    }

    /*
     * Destructor.
     * Implicitly calls ~Node<T>().
     * Resets length to 0.
     */
    ~List() {
        length = 0;
    }

    /*
     * Sets the length of the list.
     * Can only be set once when length is 0.
     */
    int setLength(unsigned int _length) {
        if (length == 0) {
            length = _length;
            this->reCreate(length);
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
    unsigned int getLength() {
        return length;
    }

    /*
     * Sets the value of an element at specified position.
     * Returns 1 on success, 0 if position is out of bounds.
     */
    int setElement(unsigned int pos, T val) {
        if (pos < length) {
            this->_Node[pos] = val;
            return 1;
        } else {
            cout << "Error: Position " << pos 
                 << " is out of bounds" << endl;
            return 0;
        }
    }

    /*
     * Gets the value of an element at specified position.
     * Uses assert to check for illegal position.
     * Prints error message and exits if position is illegal.
     */
    T getElement(unsigned int pos) {
        if (pos >= length) {
            cout << "Error: Position " << pos 
                 << " is out of bounds" << endl;
            assert(pos < length);
        }
        return this->_Node[pos];
    }

    /*
     * Assignment operator.
     * Performs deep copy from another list.
     */
    List<T>& operator=(const List<T> &other) {
        if (this != &other) {
            this->reCreate(other.length);
            length = other.length;
            for (unsigned int i = 0; i < length; i++) {
                this->_Node[i] = other._Node[i];
            }
        }
        return *this;
    }

    /*
     * Equality operator.
     * Compares two lists element by element.
     */
    inline bool operator==(const List<T> &other) {
        if (length != other.length) {
            return false;
        }
        for (unsigned int i = 0; i < length; i++) {
            if (this->_Node[i] != other._Node[i]) {
                return false;
            }
        }
        return true;
    }

    /*
     * Stream output operator.
     * Prints list length and all elements.
     */
    friend ostream& operator<<(ostream &out, List<T> list) {
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
};

#endif
