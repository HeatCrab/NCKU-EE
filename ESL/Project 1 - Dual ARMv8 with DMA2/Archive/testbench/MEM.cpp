#include "MEM.h"

void MEM::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    tlm::tlm_command  cmd    = trans.get_command();
    unsigned char*    ptr    = trans.get_data_ptr();
    unsigned int      len    = trans.get_data_length();
    sc_dt::uint64     adr    = trans.get_address() - BASE;
    unsigned int      rwData = 0;

    trans.set_response_status(tlm::TLM_OK_RESPONSE);

    if (cmd == tlm::TLM_READ_COMMAND) {
        memcpy(ptr, &mem[adr], len);
        memcpy(&rwData, ptr, len);
        std::cout << "Read  MEM 0x" << std::hex << trans.get_address()
                  << " length " << std::dec << len
                  << ": 0x" << std::hex << rwData << std::endl;
    } else if (cmd == tlm::TLM_WRITE_COMMAND) {
        memcpy(&mem[adr], ptr, len);
        memcpy(&rwData, &mem[adr], len);
        std::cout << "Write MEM 0x" << std::hex << trans.get_address()
                  << " length " << std::dec << len
                  << ": 0x" << std::hex << rwData << std::endl;
    } else {
        std::cout << "MEM receives TLM_IGNORE_COMMAND" << std::endl;
    }
}

bool MEM::verify(unsigned int src_off, unsigned int dst_off,
                 unsigned int len) const {
    bool match = (memcmp(mem + src_off, mem + dst_off, len) == 0);
    std::cout << "[VERIFY] " << (match ? "PASS" : "FAIL")
              << ": mem[0x" << std::hex << src_off
              << "] vs mem[0x" << dst_off << "]"
              << " length=" << std::dec << len << std::endl;
    return match;
}
