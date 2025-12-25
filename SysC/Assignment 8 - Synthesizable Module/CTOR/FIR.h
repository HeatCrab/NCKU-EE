#ifndef FIR_H
#define FIR_H

#define SC_INCLUDE_FX
#include <systemc.h>

SC_MODULE(FIR) {
    sc_in<bool> clk;
    sc_in<bool> rst;
    sc_in<sc_uint<32>> x;
    sc_out<sc_uint<32>> y;

    int taps;
    sc_uint<32>* coeffs;
    sc_uint<32>* buffer;

    void initialize();
    void process_fir();

    SC_CTOR(FIR) : taps(16) {
        initialize();
        SC_CTHREAD(process_fir, clk.pos());
        reset_signal_is(rst, false);
    }

    FIR(sc_module_name name, int tap_count)
        : sc_module(name), taps(tap_count) {
        initialize();
        SC_CTHREAD(process_fir, clk.pos());
        reset_signal_is(rst, false);
    }

    ~FIR() {
        delete[] coeffs;
        delete[] buffer;
    }
};

#endif
