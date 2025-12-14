//main.cpp
#include "systemc.h"
#include "HalfAdder.h"
#include "FullAdder.h"

int sc_main(int argc, char* argv[]) {

    sc_signal<bool> ha_A, ha_B, ha_Sum, ha_Cout;
    sc_signal<bool> fa_A, fa_B, fa_Cin, fa_Sum, fa_Cout;

    HalfAdder ha1("HalfAdder1");
    ha1.A(ha_A);
    ha1.B(ha_B);
    ha1.Sum(ha_Sum);
    ha1.Carry(ha_Cout);

    FullAdder fa1("FullAdder1");
    fa1.A(fa_A);
    fa1.B(fa_B);
    fa1.Cin(fa_Cin);
    fa1.S(fa_Sum);
    fa1.Cout(fa_Cout);

    // Create VCD file
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    
    // Trace signals
    sc_trace(tf, ha_A, "Half-adder_A");
    sc_trace(tf, ha_B, "Half-adder_B");
    sc_trace(tf, ha_Sum, "Half-adder_Sum");
    sc_trace(tf, ha_Cout, "Half-adder_Carry");
    
    sc_trace(tf, fa_A, "Full-adder_A");
    sc_trace(tf, fa_B, "Full-adder_B");
    sc_trace(tf, fa_Cin, "Full-adder_Cin");
    sc_trace(tf, fa_Sum, "Full-adder_S");
    sc_trace(tf, fa_Cout, "Full-adder_Cout");

    sc_start(0, SC_NS);

    // Test Half Adder
    cout << "Testing Half Adder..." << endl;
    ha_A.write(0 & 2); ha_B.write(0 & 1); sc_start(10, SC_NS);
    ha_A.write(1 & 2); ha_B.write(1 & 1); sc_start(10, SC_NS);
    ha_A.write(2 & 2); ha_B.write(2 & 1); sc_start(10, SC_NS);
    ha_A.write(3 & 2); ha_B.write(3 & 1); sc_start(10, SC_NS);

    // Test Full Adder
    cout << "Testing Full Adder..." << endl;
    fa_A.write(0 & 4); fa_B.write(0 & 2); fa_Cin.write(0 & 1); sc_start(10, SC_NS);
    fa_A.write(1 & 4); fa_B.write(1 & 2); fa_Cin.write(1 & 1); sc_start(10, SC_NS);
    fa_A.write(2 & 4); fa_B.write(2 & 2); fa_Cin.write(2 & 1); sc_start(10, SC_NS);
    fa_A.write(3 & 4); fa_B.write(3 & 2); fa_Cin.write(3 & 1); sc_start(10, SC_NS);
    fa_A.write(4 & 4); fa_B.write(4 & 2); fa_Cin.write(4 & 1); sc_start(10, SC_NS);
    fa_A.write(5 & 4); fa_B.write(5 & 2); fa_Cin.write(5 & 1); sc_start(10, SC_NS);
    fa_A.write(6 & 4); fa_B.write(6 & 2); fa_Cin.write(6 & 1); sc_start(10, SC_NS);
    fa_A.write(7 & 4); fa_B.write(7 & 2); fa_Cin.write(7 & 1); sc_start(10, SC_NS);

    sc_close_vcd_trace_file(tf);

    cout << "Simulation finished. RESULT.VCD is saved." << endl;
    return 0;
}
