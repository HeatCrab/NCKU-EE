#include "DMA.h"

void DMA::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    tlm::tlm_command cmd = trans.get_command();
    uint64_t addr = trans.get_address() - BASE; // Apply offset
    unsigned char* ptr = trans.get_data_ptr();

    if (cmd == tlm::TLM_WRITE_COMMAND) {
        switch (addr) {
            case 0x0: SOURCE = *((uint32_t*)ptr); break;
            case 0x4: TARGET = *((uint32_t*)ptr); break;
            case 0x8: SIZE   = *((uint32_t*)ptr); break;
            case 0xC: START  = (*ptr > 0); break;
        }
    }
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}

void DMA::dma_thread() {
    // Initial State / Reset
    SOURCE = 0; TARGET = 0; SIZE = 0;
    START = false;
    Interrupt.write(false);

    while (true) {
        // Wait for Start bit
        wait();
        if (START) {
            // Perform Data Movement
            for (uint32_t i = 0; i < SIZE; i += 4) {
                uint32_t buffer;
                tlm::tlm_generic_payload trans;
                sc_time delay = SC_ZERO_TIME;

                // 1. Read from Source
                trans.set_command(tlm::TLM_READ_COMMAND);
                trans.set_address(SOURCE + i);
                trans.set_data_ptr((unsigned char*)&buffer);
                trans.set_data_length(4);
                Msocket->b_transport(trans, delay);

                // 2. Write to Target
                trans.set_command(tlm::TLM_WRITE_COMMAND);
                trans.set_address(TARGET + i);
                Msocket->b_transport(trans, delay);
                
                wait(); // Simulate clock cycles for move
            }

            // Completion
            Interrupt.write(true);
            
            // Wait for Clear (0x0C = 0)
            while (START) wait();
            
            Interrupt.write(false);
        }
    }
}

