#include "MEM.h"
#include <cstring>

using namespace tlm;

void MEM::b_transport(
    tlm_generic_payload& trans,
    sc_time& delay) {
    tlm_command cmd = trans.get_command();
    uint64_t addr = trans.get_address();
    unsigned char* ptr = trans.get_data_ptr();
    uint32_t len = trans.get_data_length();

    if (addr + len > mem_size) {
        trans.set_response_status(
            TLM_ADDRESS_ERROR_RESPONSE);
        return;
    }

    if (cmd == TLM_READ_COMMAND) {
        memcpy(ptr, &mem[addr], len);
    } else if (cmd == TLM_WRITE_COMMAND) {
        memcpy(&mem[addr], ptr, len);
    }

    trans.set_response_status(TLM_OK_RESPONSE);
    wait(3);
}
