#include<systemc.h>
#include "Top.h"

int sc_main(int argc, char* argv[]){
    // Instantiate components
    Top Sys("System");

    sc_time prd = sc_time(10, SC_NS);
    sc_clock clk("clk", prd);
    sc_signal<bool> rst;

    Sys.clk(clk);
    Sys.rst(rst);

    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, Sys.int0, "INT0");
    sc_trace(tf, Sys.int1, "INT1");

    sc_trace(tf, Sys.dma->SOURCE0, "SOURCE0");
    sc_trace(tf, Sys.dma->TARGET0, "TARGET0");
    sc_trace(tf, Sys.dma->SIZE0, "SIZE0");
    sc_trace(tf, Sys.dma->START0, "START0");

    sc_trace(tf, Sys.dma->SOURCE1, "SOURCE1");
    sc_trace(tf, Sys.dma->TARGET1, "TARGET1");
    sc_trace(tf, Sys.dma->SIZE1, "SIZE1");
    sc_trace(tf, Sys.dma->START1, "START1");
    sc_trace(tf, Sys.dma->BASE, "BASE");

    sc_trace(tf, Sys.ram2->adr, "MEM2adr");
    sc_trace(tf, Sys.ram2->rdata, "MEM2rdata");
    sc_trace(tf, Sys.ram2->wdata, "MEM2wdata");
    sc_trace(tf, Sys.ram3->adr, "MEM3adr");
    sc_trace(tf, Sys.ram3->rdata, "MEM3rdata");
    sc_trace(tf, Sys.ram3->wdata, "MEM3wdata");

    sc_trace(tf, Sys.cpu0->data_source, "data_source_0");
    sc_trace(tf, Sys.cpu0->data_target, "data_target_0");
    sc_trace(tf, Sys.cpu0->data_size, "data_size_0");
    sc_trace(tf, Sys.cpu0->data_start, "data_start_0");
    sc_trace(tf, Sys.cpu0->count, "count_0");

    sc_trace(tf, Sys.cpu1->data_source, "data_source_1");
    sc_trace(tf, Sys.cpu1->data_target, "data_target_1");
    sc_trace(tf, Sys.cpu1->data_size, "data_size_1");
    sc_trace(tf, Sys.cpu1->data_start, "data_start_1");
    sc_trace(tf, Sys.cpu1->count, "count_0");

    sc_start(10, SC_NS);
    rst.write(1);
    sc_start(30, SC_NS);
    rst.write(0);
    sc_start(1000, SC_NS);

    sc_close_vcd_trace_file(tf);
    sc_stop();
	
    return 0;
}







