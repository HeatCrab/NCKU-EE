#include "FIR.h"
#include "fstream"

int sc_main(int argc, char* argv[])
{
    sc_signal<bool> rst;
    sc_time clkPrd(5, SC_NS);
    sc_clock clock("clock", 5, SC_NS);
    sc_signal<sc_uint<32> > x16, x32, x48, y16, y32, y48;
    ifstream inFile;
    int Data;

    inFile.open("firData", ios::in);

    FIR f16("FIR16");
    FIR f32("FIR32", 32);
    FIR f48("FIR48", 48);
    f16.x(x16); f16.y(y16); f16.clk(clock); f16.rst(rst);
    f32.x(x32); f32.y(y32); f32.clk(clock); f32.rst(rst);
    f48.x(x48); f48.y(y48); f48.clk(clock); f48.rst(rst);

    /* Tracing */
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clock, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, x16, "x");
    sc_trace(tf, y16, "y16");
    sc_trace(tf, y32, "y32");
    sc_trace(tf, y48, "y48");

    sc_start(0, SC_NS);
    rst.write(0);

    sc_start(20, SC_NS);
    rst.write(1);

    while(!inFile.eof()){
        inFile >> Data;
        //cout << "Data is " << Data << endl;
        x16.write(Data);
        x32.write(Data);
        x48.write(Data);
        sc_start(5, SC_NS);
    }

    sc_close_vcd_trace_file(tf);
    return 0;
}
