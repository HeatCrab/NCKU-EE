#include "Node.h"
#include <cstddef>

Node::Node() {
    _Node = NULL;
}

Node::Node(unsigned int _length) {
    _Node = new long[_length];
}

Node::~Node() {
    if (_Node != NULL) {
        delete[] _Node;
        _Node = NULL;
    }
}

long* Node::reCreate(unsigned int _length) {
    if (_Node != NULL) {
        delete[] _Node;
    }
    _Node = new long[_length];
    return _Node;
}

long* Node::getNode() {
    return _Node;
}
