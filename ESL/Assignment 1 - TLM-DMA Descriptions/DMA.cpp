#include "DMA.h"
#include <cstring>

using namespace tlm;

void DMA::b_transport(
    tlm_generic_payload& trans,
    sc_time& delay) {
    tlm_command cmd = trans.get_command();
    uint64_t addr = trans.get_address() - base_addr;
    unsigned char* ptr = trans.get_data_ptr();
    uint32_t val;

    if (cmd == TLM_WRITE_COMMAND) {
        memcpy(&val, ptr, 4);
        switch (addr) {
        case 0x0:
            source_addr = val;
            break;
        case 0x4:
            target_addr = val;
            break;
        case 0x8:
            size = val;
            break;
        case 0xC:
            start_clear = val;
            break;
        default:
            trans.set_response_status(
                TLM_ADDRESS_ERROR_RESPONSE);
            return;
        }
    } else if (cmd == TLM_READ_COMMAND) {
        switch (addr) {
        case 0x0:
            val = source_addr;
            break;
        case 0x4:
            val = target_addr;
            break;
        case 0x8:
            val = size;
            break;
        case 0xC:
            val = start_clear;
            break;
        default:
            trans.set_response_status(
                TLM_ADDRESS_ERROR_RESPONSE);
            return;
        }
        memcpy(ptr, &val, 4);
    }

    trans.set_response_status(TLM_OK_RESPONSE);
    wait(10, SC_NS);
}

void DMA::dma_thread() {
    // Reset behavior
    source_addr = 0;
    target_addr = 0;
    size = 0;
    start_clear = 0;
    state = IDLE;
    index = 0;
    interrupt.write(false);

    while (true) {
        wait();

        tlm_generic_payload trans;
        sc_time delay = SC_ZERO_TIME;

        switch (state) {
        case IDLE:
            if (start_clear == 1) {
                state = READ;
                index = 0;
            }
            break;

        case READ:
            trans.set_command(TLM_READ_COMMAND);
            trans.set_address(
                source_addr + index * 4);
            trans.set_data_ptr(data);
            trans.set_data_length(4);
            trans.set_streaming_width(4);
            trans.set_byte_enable_ptr(nullptr);
            trans.set_response_status(
                TLM_INCOMPLETE_RESPONSE);
            master->b_transport(trans, delay);
            state = WRITE;
            break;

        case WRITE:
            trans.set_command(TLM_WRITE_COMMAND);
            trans.set_address(
                target_addr + index * 4);
            trans.set_data_ptr(data);
            trans.set_data_length(4);
            trans.set_streaming_width(4);
            trans.set_byte_enable_ptr(nullptr);
            trans.set_response_status(
                TLM_INCOMPLETE_RESPONSE);
            master->b_transport(trans, delay);
            index++;
            if (index * 4 >= size) {
                state = DONE;
            } else {
                state = READ;
            }
            break;

        case DONE:
            interrupt.write(true);
            state = WAIT_CLEAR;
            break;

        case WAIT_CLEAR:
            if (start_clear == 0) {
                interrupt.write(false);
                state = IDLE;
            }
            break;
        }
    }
}
