#include "DMA.h"

void DMA::thread_process_0() {
    // Reset
    SOURCE_0 = 0;
    TARGET_0 = 0;
    SIZE_0   = 0;
    START_0  = 0;
    block_0  = false;
    intr_0   = false;
    interrupt_1.write(false);

    while (true) {
        wait();

        if (START_0) {
            if (SIZE_0 > 0) {
                // Setup transfer payload
                trans_0.set_data_ptr(trf_data_0);
                if (SIZE_0 >= 4)
                    trans_0.set_data_length(4);
                else
                    trans_0.set_data_length(SIZE_0);

                // Read from SOURCE_0
                trans_0.set_read();
                trans_0.set_address(SOURCE_0);
                master_0->b_transport(trans_0, delay);

                // Write to TARGET_0
                trans_0.set_write();
                trans_0.set_address(TARGET_0);
                master_0->b_transport(trans_0, delay);

                if (SIZE_0 > 4) {
                    SOURCE_0 += 4;
                    TARGET_0 += 4;
                    SIZE_0   -= 4;
                } else {
                    SIZE_0 = 0;
                }
                continue;
            }

            // Transfer complete — assert interrupt once
            if (!intr_0) {
                interrupt_1.write(true);
                intr_0 = true;
                std::cout << "DMA ch0 Interrupt sent" << std::endl;
            }
        } else {
            block_0 = false;   // Resume control register write
            if (intr_0) {
                interrupt_1.write(false);
                intr_0 = false;
                std::cout << "DMA ch0 clears Interrupt" << std::endl;
            }
        }
    }
}

void DMA::thread_process_1() {
    // Reset
    SOURCE_1 = 0;
    TARGET_1 = 0;
    SIZE_1   = 0;
    START_1  = 0;
    block_1  = false;
    intr_1   = false;
    interrupt_2.write(false);

    while (true) {
        wait();

        if (START_1) {
            if (SIZE_1 > 0) {
                // Setup transfer payload
                trans_1.set_data_ptr(trf_data_1);
                if (SIZE_1 >= 4)
                    trans_1.set_data_length(4);
                else
                    trans_1.set_data_length(SIZE_1);

                // Read from SOURCE_1
                trans_1.set_read();
                trans_1.set_address(SOURCE_1);
                master_1->b_transport(trans_1, delay);

                // Write to TARGET_1
                trans_1.set_write();
                trans_1.set_address(TARGET_1);
                master_1->b_transport(trans_1, delay);

                if (SIZE_1 > 4) {
                    SOURCE_1 += 4;
                    TARGET_1 += 4;
                    SIZE_1   -= 4;
                } else {
                    SIZE_1 = 0;
                }
                continue;
            }

            // Transfer complete — assert interrupt once
            if (!intr_1) {
                interrupt_2.write(true);
                intr_1 = true;
                std::cout << "DMA ch1 Interrupt sent" << std::endl;
            }
        } else {
            block_1 = false;   // Resume control register write
            if (intr_1) {
                interrupt_2.write(false);
                intr_1 = false;
                std::cout << "DMA ch1 clears Interrupt" << std::endl;
            }
        }
    }
}

void DMA::b_transport(tlm::tlm_generic_payload& trans, sc_time& r_delay) {
    wait(r_delay);

    tlm::tlm_command  cmd    = trans.get_command();
    unsigned char*    r_data = trans.get_data_ptr();
    unsigned int      r_len  = trans.get_data_length();
    sc_dt::uint64     addr   = trans.get_address() - BASE;

    trans.set_response_status(tlm::TLM_OK_RESPONSE);

    if (cmd == tlm::TLM_WRITE_COMMAND) {
        std::cout << "DMA received WRITE at 0x" << std::hex << addr + BASE
                  << " length " << std::dec << r_len << ": ";
        switch (addr) {
        case 0x00:   // SOURCE_0
            if (!block_0) {
                memcpy((unsigned char *)&SOURCE_0, r_data, r_len);
                std::cout << std::hex << "0x" << SOURCE_0 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x04:   // TARGET_0
            if (!block_0) {
                memcpy((unsigned char *)&TARGET_0, r_data, r_len);
                std::cout << std::hex << "0x" << TARGET_0 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x08:   // SIZE_0
            if (!block_0) {
                memcpy((unsigned char *)&SIZE_0, r_data, r_len);
                std::cout << std::hex << "0x" << SIZE_0 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x0C:   // START_0
            memcpy((unsigned char *)&START_0, r_data, r_len);
            std::cout << std::hex << "0x" << START_0 << std::endl;
            if (START_0 == 0x1)
                block_0 = true;
            else
                block_0 = false;
            break;
        case 0x10:   // SOURCE_1
            if (!block_1) {
                memcpy((unsigned char *)&SOURCE_1, r_data, r_len);
                std::cout << std::hex << "0x" << SOURCE_1 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x14:   // TARGET_1
            if (!block_1) {
                memcpy((unsigned char *)&TARGET_1, r_data, r_len);
                std::cout << std::hex << "0x" << TARGET_1 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x18:   // SIZE_1
            if (!block_1) {
                memcpy((unsigned char *)&SIZE_1, r_data, r_len);
                std::cout << std::hex << "0x" << SIZE_1 << std::endl;
            } else {
                trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                std::cout << "blocked" << std::endl;
            }
            break;
        case 0x1C:   // START_1
            memcpy((unsigned char *)&START_1, r_data, r_len);
            std::cout << std::hex << "0x" << START_1 << std::endl;
            if (START_1 == 0x1)
                block_1 = true;
            else
                block_1 = false;
            break;
        default:
            trans.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
            std::cout << "wrong address" << std::endl;
            break;
        }
    } else if (cmd == tlm::TLM_READ_COMMAND) {
        switch (addr) {
        case 0x00: memcpy(r_data, (unsigned char *)&SOURCE_0, r_len); break;
        case 0x04: memcpy(r_data, (unsigned char *)&TARGET_0, r_len); break;
        case 0x08: memcpy(r_data, (unsigned char *)&SIZE_0,   r_len); break;
        case 0x0C: memcpy(r_data, (unsigned char *)&START_0,  r_len); break;
        case 0x10: memcpy(r_data, (unsigned char *)&SOURCE_1, r_len); break;
        case 0x14: memcpy(r_data, (unsigned char *)&TARGET_1, r_len); break;
        case 0x18: memcpy(r_data, (unsigned char *)&SIZE_1,   r_len); break;
        case 0x1C: memcpy(r_data, (unsigned char *)&START_1,  r_len); break;
        default:   break;
        }
        std::cout << "DMA received READ at 0x" << std::hex << addr + BASE
                  << " length " << std::dec << r_len << std::endl;
    } else {
        std::cout << "DMA receives TLM_IGNORE_COMMAND" << std::endl;
    }
}
