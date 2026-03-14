#ifndef MEM_H
#define MEM_H

#include <systemc.h>
#include "tlm.h"
#include "tlm_utils/simple_target_socket.h"

SC_MODULE(MEM) {
    tlm_utils::simple_target_socket<MEM> target;

    unsigned char* mem;
    uint32_t mem_size;

    void b_transport(tlm::tlm_generic_payload& trans,
                     sc_time& delay);

    SC_CTOR(MEM)
        : target("target"), mem_size(1024) {
        mem = new unsigned char[mem_size]();
        target.register_b_transport(
            this, &MEM::b_transport);
    }

    MEM(sc_module_name name, uint32_t size)
        : sc_module(name),
          target("target"), mem_size(size) {
        mem = new unsigned char[mem_size]();
        target.register_b_transport(
            this, &MEM::b_transport);
    }

    ~MEM() {
        delete[] mem;
    }
};

#endif
