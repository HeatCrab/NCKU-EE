#ifndef FULLADDER_H
#define FULLADDER_H

#include "systemc.h"
#include "HalfAdder.h"

SC_MODULE(FullAdder) {
    sc_in <bool> A, B, Cin;     // inputs
    sc_out <bool> S, Cout;    // outputs

    sc_signal<bool> ha1_sum, ha1_carry, ha2_carry; // internal signals

    HalfAdder* ha1;
    HalfAdder* ha2;

    void compute();
    
    SC_CTOR(FullAdder) {                 // Constructor
        // Instantiate two HalfAdders
        ha1 = new HalfAdder("HalfAdder1");
        ha1->A(A);
        ha1->B(B);
        ha1->Sum(ha1_sum);
        ha1->Carry(ha1_carry);

        ha2 = new HalfAdder("HalfAdder2");
        ha2->A(ha1_sum);
        ha2->B(Cin);
        ha2->Sum(S);
        ha2->Carry(ha2_carry);

        SC_METHOD(compute);              // Register compute method
        sensitive << ha1_carry << ha2_carry;      // Sensitivity list
    }

    ~FullAdder() {
        delete ha1;
        delete ha2;
    }
};

#endif