#include "fakeUART.h"

void UART::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    adr = (trans.get_address() - BASE);
    std::cout << "UART BASE = 0x" << std::hex << BASE << " ";   
    std::cout << "UART adr = 0x" << std::hex << adr << " ";   
  
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
    return;
}

void UART::func() {
    // never activated, no sensitivity list
}
