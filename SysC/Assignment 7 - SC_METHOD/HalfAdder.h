#ifndef HALFADDER_H
#define HALFADDER_H

#include "systemc.h"

SC_MODULE(HalfAdder) {
    sc_in<bool> A;          // Input port a
    sc_in<bool> B;          // Input port b
    sc_out<bool> Sum;       // Output port sum
    sc_out<bool> Carry;     // Output port carry

    void compute();

    SC_CTOR(HalfAdder) {                    // Constructor
        SC_METHOD(compute);                 // Register compute method
        sensitive << A << B;                // Sensitivity list
    }
};

#endif