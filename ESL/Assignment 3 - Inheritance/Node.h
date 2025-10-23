#ifndef NODE_H
#define NODE_H

class Node {
protected:
    long *_Node;

public:
    Node();
    Node(unsigned int _length);
    ~Node();
    long* reCreate(unsigned int _length);
    long* getNode();
};

#endif
