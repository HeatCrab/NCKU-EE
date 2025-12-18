#include "systemc.h"
#include "FIR.h"
#include <iostream>
#include <fstream>

int sc_main(int argc, char* argv[]) {
    sc_clock clk("clk", 5, SC_NS);
    sc_signal<bool> rst;
    sc_signal<sc_uint<32>> x;
    sc_signal<sc_uint<32>> y32;
    sc_signal<sc_uint<32>> y48;

    FIR fir_inst("fir32", 32);
    fir_inst.clk(clk);
    fir_inst.rst(rst);
    fir_inst.x(x);
    fir_inst.y(y32);

    FIR fir_inst48("fir48", 48);
    fir_inst48.clk(clk);
    fir_inst48.rst(rst);
    fir_inst48.x(x);
    fir_inst48.y(y48);

    // Trace file
    sc_trace_file* tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, x, "x");
    sc_trace(tf, y32, "y32");
    sc_trace(tf, y48, "y48");

    std::ifstream input_file("firData");
    if (!input_file) {
        std::cerr << "Unable to open firData file" << std::endl;
        return 1;
    }

    // Simulation
    rst.write(0);
    x.write(0);
    sc_start(10, SC_NS); // Apply reset
    rst.write(1);
    sc_start(5, SC_NS); // Release reset

    int input_val;
    int count = 0;
    while (input_file >> input_val && count < 64) {
        x.write((sc_uint<32>)input_val);
        sc_start(5, SC_NS);
        count++;
    }

    sc_close_vcd_trace_file(tf);
    input_file.close();
    
    return 0;
}