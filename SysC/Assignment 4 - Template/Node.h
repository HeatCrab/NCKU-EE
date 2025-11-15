#ifndef NODE_H
#define NODE_H

#include <cstddef>

template <typename T>
class Node {
protected:
    T *_Node;

public:
    /*
     * Default constructor.
     * Initializes _Node as NULL.
     */
    Node() {
        _Node = NULL;
    }

    /*
     * Constructor with specified length.
     * Constructs _Node as a T array of size _length.
     */
    Node(unsigned int _length) {
        _Node = new T[_length];
    }

    /*
     * Destructor.
     * Deletes the dynamically allocated array.
     */
    ~Node() {
        if (_Node != NULL) {
            delete[] _Node;
            _Node = NULL;
        }
    }

    /*
     * Recreates the Node array with a new length.
     * Allocates for _Node a T array of size _length.
     * Returns the address of newly allocated array.
     */
    T* reCreate(unsigned int _length) {
        if (_Node != NULL) {
            delete[] _Node;
        }
        _Node = new T[_length];
        return _Node;
    }

    /*
     * Returns the pointer to the Node array.
     */
    T* getNode() {
        return _Node;
    }
};

#endif