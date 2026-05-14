#ifndef CPU_H
#define CPU_H

#include <iomanip>
#include "systemc.h"
#include "tlm.h"
#include "tlm_utils/simple_initiator_socket.h"

SC_MODULE(CPU) {
    tlm_utils::simple_initiator_socket<CPU> Msocket;

    sc_in<bool> clk;
    sc_in<bool> Reset;
    sc_in<bool> interrupt_1;
    sc_in<bool> interrupt_2;

    // DMA2 register shadow (for tracing)
    sc_uint<32> data_source_0, data_target_0, data_size_0, data_start_0;
    sc_uint<32> data_source_1, data_target_1, data_size_1, data_start_1;

    tlm::tlm_generic_payload trans_m;
    sc_time delay = sc_time(10, SC_NS);

    void startCPU();

    SC_CTOR(CPU) : Msocket("Msocket") {
        SC_THREAD(startCPU);
        sensitive << clk.pos() << Reset.pos();
    }
};

#endif
