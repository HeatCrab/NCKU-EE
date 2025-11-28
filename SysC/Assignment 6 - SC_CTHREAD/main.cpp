//main.cpp
#include <systemc.h>
#include "timer.h"

int sc_main(int argc, char* argv[]) {

    FILE *fp_o;
    int i;

    sc_signal<bool> start;
    sc_signal<bool> timeout;
    sc_time clkPrd(10, SC_NS);
    sc_clock clock("clock", clkPrd, 0.5, SC_ZERO_TIME, true);

    timer f1("Timer");

    // output, clock and reset
    f1.start(start);
    f1.timeout(timeout);
    f1.clock(clock);

    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clock, "clock");
    sc_trace(tf, start, "start");
    sc_trace(tf, timeout, "timeout");
    sc_trace(tf, f1.count, "count");

    sc_start(0, SC_NS);
    start.write(0);
    sc_start(clkPrd*2);
    start.write(1);
    sc_start(clkPrd);
    start.write(0);
    sc_start(clkPrd*3);
    start.write(1);
    sc_start(clkPrd);
    start.write(0);
    sc_start(clkPrd*6);
    start.write(1);
    sc_start(clkPrd);
    start.write(0);
    sc_start(clkPrd*5);
 
    cout << "Timer done\n" << endl;
    sc_close_vcd_trace_file(tf);

    return(0);
}
