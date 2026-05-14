#ifndef SYSTEMC_INCLUDE_PJ1BUS0_H
#define SYSTEMC_INCLUDE_PJ1BUS0_H

#include <systemc.h>
#include <tlm.h>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/simple_target_socket.h>

// Define the Bus as a standard SC_MODULE
class PJ1Bus0: public sc_module {
public:
    // Multi-sockets allow multiple connections to a single bus instance
    tlm_utils::simple_initiator_socket<PJ1Bus0> Msocket0;
    tlm_utils::simple_initiator_socket<PJ1Bus0> Msocket1;
    tlm_utils::simple_target_socket<PJ1Bus0>    Ssocket;

    sc_in<bool>  clk;
    sc_in<bool>  rst;

    void pj1bus0_proc();

    PJ1Bus0(sc_module_name name) : Msocket0("Msocket0"),
                                   Msocket1("Msocket1"),
                                   Ssocket("Ssocket") {
        // Register the callback for forward transactions
        Ssocket.register_b_transport(this, &PJ1Bus0::b_transport);
        SC_CTHREAD(pj1bus0_proc, clk.pos());
        reset_signal_is(rst, true);
    }

    // This function will be overridden or customized in the Top module 
    // to define specific routing for Bus1, Bus2, and Bus3.
    virtual void b_transport(tlm::tlm_generic_payload&, sc_time&);
};
#endif /* SYSTEMC_INCLUDE_PJ1BUS0_H */
