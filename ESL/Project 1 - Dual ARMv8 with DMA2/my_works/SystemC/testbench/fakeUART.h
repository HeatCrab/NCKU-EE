#ifndef UART_H
#define UART_H

// Needed for the simple_target_socket
// #define SC_INCLUDE_DYNAMIC_PROCESSES

#include <systemc.h>
using namespace sc_core;
using namespace sc_dt;
using namespace std;
// using namespace tlm;
#include <tlm.h>
#include <tlm_utils/simple_target_socket.h>

SC_MODULE(UART){
    tlm_utils::simple_target_socket<UART> Ssocket;

    void func();
    void b_transport(tlm::tlm_generic_payload&, sc_time&);

    sc_dt::uint64 adr;

    SC_CTOR(UART, sc_uint<32> base_) : BASE(base_), Ssocket("Ssocket") {
        Ssocket.register_b_transport(this, &UART::b_transport);
        SC_METHOD(func);
    }
private:
    sc_dt::uint64 BASE = 0;
};


#endif
