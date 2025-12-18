#ifndef FIR_H
#define FIR_H

#include <systemc.h>
#include <sysc/datatypes/fx/sc_fixed.h>
#include <vector>

SC_MODULE(FIR) {
    sc_in<bool> clk;
    sc_in<bool> rst;
    sc_in<sc_uint<32>> x;
    sc_out<sc_uint<32>> y;

    const unsigned int tap;
    
    // Internal storage for coefficients and shift registers
    std::vector<sc_uint<32>> regs;
    std::vector<sc_uint<32>> b;

    void process_fir();

    SC_HAS_PROCESS(FIR);

    FIR(sc_module_name name, unsigned int n = 16)
        : sc_module(name), tap(n)
    {
        SC_CTHREAD(process_fir, clk.pos());
        reset_signal_is(rst, false);

        // Initialize vectors here to prevent segmentation faults
        regs.resize(tap, 0);
        b.resize(tap, 0);
    }
};

#endif // FIR_H