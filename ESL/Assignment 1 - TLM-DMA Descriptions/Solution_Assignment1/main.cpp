#include <systemc.h>
#include <cstring>
#include <iostream>
#include "DMA.h"
#include "CPU.h"
#include "MEM.h"

using namespace std;

int sc_main(int argc, char* argv[]) {
    sc_clock clk("clk", 5, SC_NS);
    sc_signal<bool> rst;
    sc_signal<bool> irq;

    uint32_t dma_base = 0x10000000;

    DMA dma("dma", dma_base);
    CPU cpu("cpu");
    MEM mem("mem", 2048);

    // Connect DMA signals
    dma.clk(clk);
    dma.reset(rst);
    dma.interrupt(irq);

    // CPU -> DMA slave
    cpu.master(dma.slave);
    cpu.interrupt(irq);

    // DMA master -> MEM
    dma.master(mem.target);

    // Initialize source memory with test data
    for (uint32_t i = 0; i < 8; i++) {
        uint32_t val = (i + 1) * 100;
        memcpy(&mem.mem[i * 4], &val, 4);
    }

    // Trace waveforms
    sc_trace_file* tf =
        sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, irq, "interrupt");
    sc_trace(tf, dma.state, "dma_state");
    sc_trace(tf, dma.source_addr,
             "dma_source_addr");
    sc_trace(tf, dma.target_addr,
             "dma_target_addr");
    sc_trace(tf, dma.size, "dma_size");
    sc_trace(tf, dma.start_clear,
             "dma_start_clear");

    // Reset sequence
    rst.write(false);
    sc_start(10, SC_NS);
    rst.write(true);

    // Run simulation
    sc_start(500, SC_NS);

    // Verify transfer
    cout << "\n[Verify] Checking memory..."
              << endl;
    bool pass = true;
    for (uint32_t i = 0; i < 8; i++) {
        uint32_t src_val, tgt_val;
        memcpy(&src_val, &mem.mem[i * 4], 4);
        memcpy(&tgt_val,
               &mem.mem[0x200 + i * 4], 4);
        cout << "  src[" << i << "] = "
                  << src_val << ", tgt[" << i
                  << "] = " << tgt_val << endl;
        if (src_val != tgt_val) {
            pass = false;
        }
    }
    cout << "[Verify] "
              << (pass ? "PASS" : "FAIL")
              << endl;

    sc_close_vcd_trace_file(tf);
    return 0;
}
