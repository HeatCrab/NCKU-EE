#ifndef FIR_MODULE
#define FIR_MODULE
#define SC_INCLUDE_FX
#include "systemc.h"

SC_MODULE(FIR)
{
    sc_in<sc_uint<32> > x;
    sc_out<sc_uint<32> > y;
    sc_in<bool> clk, rst;

    sc_uint<32> sum;
    sc_fixed<32, 16> fb;
    sc_uint<32> b;

    void fir();

    SC_CTOR(FIR, unsigned int tap_ = 16) :
            tap(tap_)
    {
        SC_CTHREAD(fir, clk.pos());
        reset_signal_is(rst, false);

        mid = new sc_signal<sc_uint<32> > [tap];
        fb_cal();	// To compute b, not real circuits
    }
private:
    sc_signal<sc_uint<32> > *mid;
    const unsigned int tap;
    void fb_cal();
};
#endif
