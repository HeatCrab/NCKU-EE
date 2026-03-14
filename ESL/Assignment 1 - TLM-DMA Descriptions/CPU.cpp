#include "CPU.h"
#include <cstring>
#include <iostream>

using namespace std;
using namespace tlm;

void CPU::write_dma(uint32_t addr, uint32_t data) {
    tlm_generic_payload trans;
    sc_time delay = SC_ZERO_TIME;
    unsigned char buf[4];

    memcpy(buf, &data, 4);
    trans.set_command(TLM_WRITE_COMMAND);
    trans.set_address(addr);
    trans.set_data_ptr(buf);
    trans.set_data_length(4);
    trans.set_streaming_width(4);
    trans.set_byte_enable_ptr(nullptr);
    trans.set_response_status(
        TLM_INCOMPLETE_RESPONSE);

    master->b_transport(trans, delay);
}

void CPU::cpu_thread() {
    // Wait for simulation to settle
    wait(10, SC_NS);

    uint32_t dma_base = 0x10000000;
    uint32_t src_addr = 0x0;
    uint32_t tgt_addr = 0x200;
    uint32_t xfer_size = 8;

    cout << "[CPU] Configuring DMA:" << endl;
    cout << "  Source = 0x" << hex
              << src_addr << endl;
    cout << "  Target = 0x" << tgt_addr
              << endl;
    cout << "  Size   = " << dec
              << xfer_size << " words" << endl;

    // Write control registers
    write_dma(dma_base + 0x0, src_addr);
    write_dma(dma_base + 0x4, tgt_addr);
    write_dma(dma_base + 0x8, xfer_size);
    write_dma(dma_base + 0xC, 1);

    cout << "[CPU] DMA started, waiting for "
              << "interrupt..." << endl;

    // Wait for interrupt
    while (interrupt.read() == false) {
        wait(5, SC_NS);
    }

    cout << "[CPU] Interrupt received, "
              << "clearing..." << endl;

    // Clear interrupt
    write_dma(dma_base + 0xC, 0);

    wait(10, SC_NS);
    cout << "[CPU] Done." << endl;
}
