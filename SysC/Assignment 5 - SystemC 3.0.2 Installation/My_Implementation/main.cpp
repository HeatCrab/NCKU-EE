//main.cpp
#include <systemc.h>
#include "timer.h"

int sc_main(int argc, char* argv[]) {

    // ======================
    //  Signals
    // ======================
    sc_signal<bool> start;
    sc_signal<bool> timeout;

    // 100 MHz clock = 10 ns period
    sc_clock clock("clock", 10, SC_NS);

    // ======================
    //  Instantiate timer
    // ======================
    timer tm("tm");
    tm.start(start);
    tm.timeout(timeout);
    tm.clock(clock);

    // ======================
    //  Create trace file
    // ======================
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clock, "clock");
    sc_trace(tf, start, "start");
    sc_trace(tf, timeout, "timeout");
    sc_trace(tf, tm.count, "count");

    // ======================
    //  Stimulus generation
    //  Total: 30 clock cycles (300 ns)
    // ======================

    // Initialize
    sc_start(0, SC_NS);
    start.write(0);

    // Scenario 1: Reset timer for 3 cycles before release
    // Cycles 1-3: start=0 (reset for 3 cycles)
    sc_start(30, SC_NS);     // 3 cycles * 10 ns

    // Cycles 4-8: start=1 (counting down from 5)
    start.write(1);
    sc_start(50, SC_NS);     // 5 cycles * 10 ns

    // Scenario 2: Reset during counting before count reaches 0
    // Cycles 9-10: start=0 (reset before count reaches 0)
    start.write(0);
    sc_start(20, SC_NS);     // 2 cycles * 10 ns

    // Cycles 11-15: start=1 (counting down from 5 again)
    start.write(1);
    sc_start(50, SC_NS);     // 5 cycles * 10 ns

    // Scenario 3: Reset during counting after count reaches 0
    // Cycles 16-20: wait for count to reach 0 (5 more cycles)
    // The count should reach 0 around cycle 20
    sc_start(50, SC_NS);     // 5 cycles * 10 ns

    // Cycles 21-22: start=0 (reset after count reached 0)
    start.write(0);
    sc_start(20, SC_NS);     // 2 cycles * 10 ns

    // Cycles 23-30: Remaining cycles to complete 30 total
    sc_start(80, SC_NS);     // 8 cycles * 10 ns

    cout << "Timer simulation completed - 30 cycles (300 ns)" << endl;
    sc_close_vcd_trace_file(tf);

    return(0);
}
