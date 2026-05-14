#ifndef SYSTEMC_INCLUDE_PJ1BUS1_H
#define SYSTEMC_INCLUDE_PJ1BUS1_H

#include <systemc.h>
#include <tlm.h>
#include "tlm_utils/simple_initiator_socket.h"
#include "tlm_utils/simple_target_socket.h"

// Define the Bus as a standard SC_MODULE
class PJ1Bus1: public sc_module {
public:
    // Multi-sockets allow multiple connections to a single bus instance
    tlm_utils::simple_initiator_socket<PJ1Bus1> Msocket0;  // M of DMA2
    tlm_utils::simple_initiator_socket<PJ1Bus1> Msocket1;  // M of DRAM2
    tlm_utils::simple_initiator_socket<PJ1Bus1> Msocket2;  // M of DRAM3
    tlm_utils::simple_initiator_socket<PJ1Bus1> Msocket3;  // M of UART0
    tlm_utils::simple_initiator_socket<PJ1Bus1> Msocket4;  // M of UART1
    tlm_utils::simple_target_socket<PJ1Bus1>    Ssocket0;
    tlm_utils::simple_target_socket<PJ1Bus1>    Ssocket1;
    tlm_utils::simple_target_socket<PJ1Bus1>    Ssocket2;
    tlm_utils::simple_target_socket<PJ1Bus1>    Ssocket3;

    sc_in<bool>  clk;
    sc_in<bool>  rst;

    void pj1bus1_proc();

    PJ1Bus1(sc_module_name name) : Msocket0("Msocket0"),
                                   Msocket1("Msocket1"),
                                   Msocket2("Msocket2"),
                                   Msocket3("Msocket3"),
                                   Msocket4("Msocket4"),
                                   Ssocket0("Ssocket0"),
                                   Ssocket1("Ssocket1"),
                                   Ssocket2("Ssocket2"),
                                   Ssocket3("Ssocket3") {
        // Register the callback for forward transactions
        Ssocket0.register_b_transport(this, &PJ1Bus1::b_transport0);
        Ssocket1.register_b_transport(this, &PJ1Bus1::b_transport1);
        Ssocket2.register_b_transport(this, &PJ1Bus1::b_transport2);
        Ssocket3.register_b_transport(this, &PJ1Bus1::b_transport3);
        SC_CTHREAD(pj1bus1_proc, clk.pos());
        reset_signal_is(rst, true);
    }

    // This function will be overridden or customized in the Top module 
    // to define specific routing for Bus1, Bus2, and Bus3.
    virtual void b_transport0(tlm::tlm_generic_payload&, sc_time&);
    virtual void b_transport1(tlm::tlm_generic_payload&, sc_time&);
    virtual void b_transport2(tlm::tlm_generic_payload&, sc_time&);
    virtual void b_transport3(tlm::tlm_generic_payload&, sc_time&);
};
#endif /* SYSTEMC_INCLUDE_PJ1BUS1_H */
