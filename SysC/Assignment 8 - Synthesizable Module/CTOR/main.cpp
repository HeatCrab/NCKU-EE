#define SC_INCLUDE_FX
#include "systemc.h"
#include "FIR.h"
#include <fstream>
#include <iostream>

int sc_main(int argc, char* argv[]) {
    sc_clock clk("clk", 5, SC_NS);
    sc_signal<bool> rst;
    sc_signal<sc_uint<32>> x;
    sc_signal<sc_uint<32>> y32, y48;

    FIR fir32("fir32", 32);
    FIR fir48("fir48", 48);

    fir32.clk(clk);
    fir32.rst(rst);
    fir32.x(x);
    fir32.y(y32);

    fir48.clk(clk);
    fir48.rst(rst);
    fir48.x(x);
    fir48.y(y48);

    sc_trace_file* tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, x, "x");
    sc_trace(tf, y32, "y32");
    sc_trace(tf, y48, "y48");

    rst.write(false);
    sc_start(10, SC_NS);
    rst.write(true);

    std::ifstream inputFile("firData");
    if (!inputFile) {
        std::cerr << "Error: Cannot open input file 'firData'." << std::endl;
        return 1;
    }

    sc_uint<32> inputData;
    for (int i = 0; i < 64; ++i) {
        if (!(inputFile >> inputData)) {
            std::cerr << "Error: Insufficient data in input file." << std::endl;
            break;
        }
        x.write(inputData);
        sc_start(5, SC_NS);
    }
    inputFile.close();

    sc_close_vcd_trace_file(tf);
    return 0;
}
