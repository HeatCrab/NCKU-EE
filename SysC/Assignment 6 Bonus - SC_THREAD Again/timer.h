#include "systemc.h"

SC_MODULE(timer) {
    sc_in<bool> start;				// ports
    sc_out<bool> timeout;
    sc_in<bool> clock;

    int count;					// data and function members
    void runtimer();

    SC_CTOR(timer) {				// constructor
        SC_THREAD(runtimer);
        sensitive << clock.pos()		// sensitivity list
                  << start;
        count = 0;
    }
};
