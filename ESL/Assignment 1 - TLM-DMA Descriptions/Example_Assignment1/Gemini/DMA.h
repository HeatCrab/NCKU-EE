#ifndef DMA_H
#define DMA_H

#include <systemc.h>
#include <tlm.h>
#include "tlm_utils/simple_initiator_socket.h"
#include "tlm_utils/simple_target_socket.h"

SC_MODULE(DMA) {
    // Ports
    tlm_utils::simple_target_socket<DMA>    Ssocket;    // For CPU config
    tlm_utils::simple_initiator_socket<DMA> Msocket;    // For data move
    sc_in<bool>   Reset;
    sc_in<bool>   clk;
    sc_out<bool>  Interrupt;

    // Internal Registers
    uint32_t SOURCE;    // 0x0
    uint32_t TARGET;    // 0x4
    uint32_t SIZE;      // 0x8
    bool     START;     // 0xC
    uint32_t BASE;      // Static base address

    void dma_thread();
    virtual void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay);

    SC_CTOR(DMA) : Ssocket("Ssocket"),
                   Msocket("Msocket"), BASE(0x100000) {
        Ssocket.register_b_transport(this, &DMA::b_transport);
        
        SC_CTHREAD(dma_thread, clk.pos());
        reset_signal_is(Reset, false); // Active low reset
    }
};

#endif

