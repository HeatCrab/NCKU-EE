#include "PJ1Bus1.h"

// slave port of ARMv8_0
void PJ1Bus1::b_transport0(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    // Default: Forward to the first connected initiator (id 0)
    sc_dt::uint64 addr = trans.get_address();
    if (addr >= 0x100000 && addr < 0x10001F)
        Msocket0->b_transport(trans, delay);
    else if (addr >= 0x200000 && addr < 0x2FFFFF)
        Msocket1->b_transport(trans, delay);
    else if (addr >= 0x300000 && addr < 0x3FFFFF)
        Msocket2->b_transport(trans, delay);
    else if (addr >= 0x400000 && addr < 0x400FFF)
        Msocket3->b_transport(trans, delay);
    else if (addr >= 0x401000 && addr < 0x401FFF)
        Msocket3->b_transport(trans, delay);
    else {
        std::cout << "Bus1 address out of range: 0x"
                  << std::hex << addr << std::endl;
        sc_stop();
    }
}

// slave port of ARMv8_1
void PJ1Bus1::b_transport1(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    // Default: Forward to the first connected initiator (id 0)
    sc_dt::uint64 addr = trans.get_address();
    if (addr >= 0x100000 && addr < 0x10001F)
        Msocket0->b_transport(trans, delay);
    else if (addr >= 0x200000 && addr < 0x2FFFFF)
        Msocket1->b_transport(trans, delay);
    else if (addr >= 0x300000 && addr < 0x3FFFFF)
        Msocket2->b_transport(trans, delay);
    else if (addr >= 0x400000 && addr < 0x400FFF)
        Msocket4->b_transport(trans, delay);
    else if (addr >= 0x401000 && addr < 0x401FFF)
        Msocket3->b_transport(trans, delay);
    else {
        std::cout << "Bus1 address out of range: 0x"
                  << std::hex << addr << std::endl;
        sc_stop();
    }
}

// slave port of DMA2 Msocket[0] 
void PJ1Bus1::b_transport2(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    // Default: Forward to the first connected initiator (id 0)
    sc_dt::uint64 addr = trans.get_address();
    if (addr >= 0x200000 && addr < 0x2FFFFF)
        Msocket1->b_transport(trans, delay);
    else if (addr >= 0x300000 && addr < 0x3FFFFF)
        Msocket2->b_transport(trans, delay);
    else if (addr >= 0x400000 && addr < 0x400FFF)
        Msocket3->b_transport(trans, delay);
    else if (addr >= 0x401000 && addr < 0x401FFF)
        Msocket4->b_transport(trans, delay);
    else {
        std::cout << "Bus1 address out of range: 0x"
                  << std::hex << addr << std::endl;
        sc_stop();
    }
}

// slave port of DMA2 Msocket[1] 
void PJ1Bus1::b_transport3(tlm::tlm_generic_payload& trans, sc_time& delay) {
    wait(delay);

    // Default: Forward to the first connected initiator (id 0)
    sc_dt::uint64 addr = trans.get_address();
    if (addr >= 0x200000 && addr < 0x2FFFFF)
        Msocket1->b_transport(trans, delay);
    else if (addr >= 0x300000 && addr < 0x3FFFFF)
        Msocket2->b_transport(trans, delay);
    else if (addr >= 0x400000 && addr < 0x400FFF)
        Msocket3->b_transport(trans, delay);
    else if (addr >= 0x401000 && addr < 0x401FFF)
        Msocket4->b_transport(trans, delay);
    else {
        std::cout << "Bus1 address out of range: 0x"
                  << std::hex << addr << std::endl;
        sc_stop();
    }
}

void PJ1Bus1::pj1bus1_proc() {
    // no reset behavior
    while (1) {
        wait();
    }
}
