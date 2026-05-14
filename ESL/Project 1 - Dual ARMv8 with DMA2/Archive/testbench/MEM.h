#ifndef MEM_H
#define MEM_H

#include <systemc.h>
#include <tlm.h>
#include <tlm_utils/simple_target_socket.h>

SC_MODULE(MEM) {
    tlm_utils::simple_target_socket<MEM> Ssocket;

    void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay);

    // Compare src_off region vs dst_off region for len bytes
    bool verify(unsigned int src_off, unsigned int dst_off,
                unsigned int len) const;

    SC_CTOR(MEM, sc_dt::uint64 base_, unsigned int size_)
        : Ssocket("Ssocket"), BASE(base_), SIZE(size_) {
        Ssocket.register_b_transport(this, &MEM::b_transport);
        mem = new unsigned char[SIZE]();    // zero-initialised
        // Fill lower half with incrementing pattern (used as source area)
        for (unsigned int i = 0; i < SIZE / 2; i++)
            mem[i] = (unsigned char)(i % 256);
    }

    ~MEM() { delete[] mem; }

private:
    sc_dt::uint64  BASE;
    unsigned int   SIZE;
    unsigned char* mem;
};

#endif
