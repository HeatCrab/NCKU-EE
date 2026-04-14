#ifndef CPU_H
#define CPU_H

#include <systemc.h>
#include "tlm.h"
#include "tlm_utils/simple_initiator_socket.h"

SC_MODULE(CPU) {
    tlm_utils::simple_initiator_socket<CPU> master;
    sc_in<bool> interrupt;

    void cpu_thread();
    void write_dma(uint32_t addr, uint32_t data);

    SC_CTOR(CPU) : master("master") {
        SC_THREAD(cpu_thread);
    }
};

#endif
