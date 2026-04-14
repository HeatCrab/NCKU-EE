#include "DMA.h"

// Simple Memory Module
struct Memory : sc_module {
    tlm_utils::simple_target_socket<Memory> tsock;
    uint32_t mem[1024];

    SC_CTOR(Memory) : tsock("tsock") {
        tsock.register_b_transport(this, &Memory::b_transport);
    }

    void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
        uint64_t addr = trans.get_address() / 4;
        if (trans.get_command() == tlm::TLM_WRITE_COMMAND)
            mem[addr] = *((uint32_t*)trans.get_data_ptr());
        else
            *((uint32_t*)trans.get_data_ptr()) = mem[addr];
        trans.set_response_status(tlm::TLM_OK_RESPONSE);
    }
};

// Fake CPU to trigger DMA
struct CPU : sc_module {
    tlm_utils::simple_initiator_socket<CPU> isock;
    sc_in<bool> irq;

    void drive_dma() {
        uint32_t data;
        sc_time delay = SC_ZERO_TIME;
        tlm::tlm_generic_payload trans;

        auto send_write = [&](uint64_t addr, uint32_t val) {
            trans.set_command(tlm::TLM_WRITE_COMMAND);
            trans.set_address(addr);
            trans.set_data_ptr((unsigned char*)&val);
            trans.set_data_length(4);
            isock->b_transport(trans, delay);
        };

        wait(10, SC_NS);
        send_write(0x100000, 0x000); // Source
        wait(10, SC_NS);
        send_write(0x100004, 0x100); // Target
        wait(10, SC_NS);
        send_write(0x100008, 0x10);  // Size (16 bytes)
        wait(10, SC_NS);
        send_write(0x10000C, 1);     // START

        while (!irq.read()) wait(10, SC_NS);  // Wait for Interrupt
        cout << "DMA Finished at " << sc_time_stamp() << endl;
 
        send_write(0x10000C, 0);     // CLEAR
    }

    SC_CTOR(CPU) : isock("isock") { SC_THREAD(drive_dma); }
};

int sc_main(int argc, char* argv[]) {
    sc_clock clk("clk", 10, SC_NS);
    sc_signal<bool> rst, irq;

    CPU cpu("CPU");
    DMA dma("DMA");
    Memory mem("MEM");

    cpu.isock.bind(dma.Ssocket);
    dma.Msocket.bind(mem.tsock);
    cpu.irq(irq);
    dma.Interrupt(irq);
    dma.clk(clk);
    dma.Reset(rst);

    // Waveform Trace
    sc_trace_file *tf = sc_create_vcd_trace_file("RESULT");
    sc_trace(tf, clk, "clk");
    sc_trace(tf, rst, "rst");
    sc_trace(tf, irq, "interrupt");
    sc_trace(tf, dma.SOURCE, "SOURCE");
    sc_trace(tf, dma.TARGET, "TARGET");
    sc_trace(tf, dma.SIZE, "SIZE");
    sc_trace(tf, dma.START, "START");

    rst.write(false); sc_start(20, SC_NS); rst.write(true);
    sc_start(500, SC_NS);
    
    sc_close_vcd_trace_file(tf);
    return 0;
}

