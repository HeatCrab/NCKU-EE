#include "FIR.h"
#include "fstream"

int sc_main(int argc, char* argv[])
{
    sc_signal<bool> rst;
    sc_clock clock("clock", 5, SC_NS);  // 200MHz
    sc_signal<sc_uint<32> > x, y;
    ifstream inFile;
    int Data;

    inFile.open("firData", ios::in);

    FIR fir("fir");
    fir.x(x);
    fir.y(y);
    fir.clk(clock);
    fir.rst(rst);

    /* Tracing */
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clock, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, x, "x");
    sc_trace(tf, y, "y");

    sc_start(0, SC_NS);
    rst.write(0);

    sc_start(20, SC_NS);
    rst.write(1);

    while(!inFile.eof()){
        inFile >> Data;
        x.write(Data);
        sc_start(5, SC_NS);
    }

    sc_close_vcd_trace_file(tf);
    return 0;
}
