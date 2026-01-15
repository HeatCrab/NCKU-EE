#ifndef FIR_MODULE
#define FIR_MODULE
#include "systemc.h"

SC_MODULE(FIR)
{
    sc_in<sc_uint<32> > x;
    sc_out<sc_uint<32> > y;
    sc_in<bool> clk, rst;

    sc_uint<32> sum;
    sc_uint<32> b;

    void fir();

    SC_CTOR(FIR)
    {
        SC_CTHREAD(fir, clk.pos());
        reset_signal_is(rst, false);

        b = 0x000007C1;  // Fixed coefficient for 32-order FIR
    }
private:
    sc_signal<sc_uint<32> > mid[32];  // 32 delays
};
#endif
