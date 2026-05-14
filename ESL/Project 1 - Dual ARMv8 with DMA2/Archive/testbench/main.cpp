#include "../DMA.h"
#include "MEM.h"
#include "CPU.h"
#include <systemc.h>

int sc_main(int argc, char* argv[]) {
    // ── Instantiate components ──
    DMA *dma  = new DMA("dma");
    // MEM_0: 8KB at 0x200000 — used by DMA2 master_0
    //   source area: 0x200000~0x2000FF (first 256B, pre-filled)
    //   target area: 0x201000~0x2010FF (at offset 0x1000, zero-init)
    MEM *mem0 = new MEM("mem0", 0x200000, 0x2000);
    // MEM_1: 8KB at 0x300000 — used by DMA2 master_1
    MEM *mem1 = new MEM("mem1", 0x300000, 0x2000);
    CPU *cpu  = new CPU("cpu");

    sc_time prd = sc_time(10, SC_NS);
    sc_clock clk("clk", prd);
    sc_signal<bool> interrupt_1, interrupt_2, Reset;

    // ── Clock / reset / interrupt connections ──
    dma->clk(clk);
    dma->reset(Reset);
    dma->interrupt_1(interrupt_1);
    dma->interrupt_2(interrupt_2);

    cpu->clk(clk);
    cpu->Reset(Reset);
    cpu->interrupt_1(interrupt_1);
    cpu->interrupt_2(interrupt_2);

    // ── TLM socket bindings ──
    cpu->Msocket.bind(dma->slave);
    dma->master_0.bind(mem0->Ssocket);
    dma->master_1.bind(mem1->Ssocket);

    // ── VCD trace ──
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk,         "clk");
    sc_trace(tf, Reset,       "Reset");
    sc_trace(tf, interrupt_1, "interrupt_1");
    sc_trace(tf, interrupt_2, "interrupt_2");
    sc_trace(tf, dma->SOURCE_0, "SOURCE_0");
    sc_trace(tf, dma->TARGET_0, "TARGET_0");
    sc_trace(tf, dma->SIZE_0,   "SIZE_0");
    sc_trace(tf, dma->START_0,  "START_0");
    sc_trace(tf, dma->SOURCE_1, "SOURCE_1");
    sc_trace(tf, dma->TARGET_1, "TARGET_1");
    sc_trace(tf, dma->SIZE_1,   "SIZE_1");
    sc_trace(tf, dma->START_1,  "START_1");
    sc_trace(tf, cpu->data_source_0, "cpu_source_0");
    sc_trace(tf, cpu->data_target_0, "cpu_target_0");
    sc_trace(tf, cpu->data_start_0,  "cpu_start_0");
    sc_trace(tf, cpu->data_source_1, "cpu_source_1");
    sc_trace(tf, cpu->data_target_1, "cpu_target_1");
    sc_trace(tf, cpu->data_start_1,  "cpu_start_1");

    // ── Simulation ──
    sc_start(10, SC_NS);
    Reset.write(1);
    sc_start(10, SC_NS);
    Reset.write(0);
    sc_start(5000, SC_NS);

    // ── Verify transfers ──
    std::cout << "\n=== Transfer Verification ===" << std::endl;
    mem0->verify(0x0000, 0x1000, 256);   // ch0: src[0] -> dst[0x1000]
    mem1->verify(0x0000, 0x1000, 256);   // ch1: src[0] -> dst[0x1000]

    sc_close_vcd_trace_file(tf);
    sc_stop();

    return 0;
}
