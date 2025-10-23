#ifndef LIST_H
#define LIST_H

#include "Node.h"
#include <iostream>
using namespace std;

class List : public Node {
private:
    unsigned int length;

public:
    List();
    List(unsigned int _length);
    List(const List &other);
    ~List();
    List& operator=(const List& other);
    int setLength(unsigned int);
    unsigned int getLength();
    int setElement(unsigned int pos, long val);
    long getElement(unsigned int pos);
    List operator+(const List &);
    List& operator+=(const List &);
    List operator++();
    List operator++(int);
    List operator--();
    List operator--(int);
    friend ostream& operator<<(ostream &, List);
    friend istream& operator>>(istream &, List &);
};

#endif
