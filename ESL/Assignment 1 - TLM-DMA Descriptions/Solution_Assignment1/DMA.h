#ifndef DMA_H
#define DMA_H

#include <systemc.h>
#include "tlm.h"
#include "tlm_utils/simple_initiator_socket.h"
#include "tlm_utils/simple_target_socket.h"

SC_MODULE(DMA) {
    tlm_utils::simple_initiator_socket<DMA> master;
    tlm_utils::simple_target_socket<DMA> slave;

    sc_out<bool> interrupt;
    sc_in<bool> reset;
    sc_in<bool> clk;

    enum State {
        IDLE, READ, WRITE, DONE, WAIT_CLEAR
    };

    uint32_t source_addr;
    uint32_t target_addr;
    uint32_t size;
    uint32_t start_clear;
    uint32_t base_addr;

    int state;
    uint32_t index;
    unsigned char data[4];

    void dma_thread();
    void b_transport(tlm::tlm_generic_payload& trans,
                     sc_time& delay);

    SC_CTOR(DMA)
        : master("master"), slave("slave"),
          base_addr(0) {
        slave.register_b_transport(
            this, &DMA::b_transport);
        SC_CTHREAD(dma_thread, clk.pos());
        reset_signal_is(reset, false);
    }

    DMA(sc_module_name name, uint32_t base)
        : sc_module(name),
          master("master"), slave("slave"),
          base_addr(base) {
        slave.register_b_transport(
            this, &DMA::b_transport);
        SC_CTHREAD(dma_thread, clk.pos());
        reset_signal_is(reset, false);
    }
};

#endif
