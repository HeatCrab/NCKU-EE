#include "PJ1Bus0.h"

void PJ1Bus0::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    // Default: Forward to the first connected initiator (id 0)
    sc_dt::uint64 addr = trans.get_address();
    if (addr < 0xFFFFF)
        Msocket0->b_transport(trans, delay);
    else if (addr >= 0x100000 && addr < 0x500000)
        Msocket1->b_transport(trans, delay);
    else {
        std::cout << "Bus0 address out of range: 0x"
                  << std::hex << addr << std::endl;
        sc_stop();
    }
}

void PJ1Bus0::pj1bus0_proc() {
    // no reset behavior
    while (1) {
        wait();
    }
}
