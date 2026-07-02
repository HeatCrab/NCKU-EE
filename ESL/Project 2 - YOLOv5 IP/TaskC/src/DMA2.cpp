#include "DMA2.h"

void DMA2::b_transport(tlm::tlm_generic_payload& trans, sc_time& r_delay) {
    wait(r_delay);

    // Assumes all control registers are accessed as full 32-bit words
    tlm::tlm_command cmd_r = trans.get_command();
    unsigned char* r_data = trans.get_data_ptr();
    unsigned int r_len = trans.get_data_length();
    sc_dt::uint64 addr = trans.get_address();

    // Set OK status first, and change if anything goes otherwise
    trans.set_response_status(tlm::TLM_OK_RESPONSE);

    // Reading and writing control registers based on address.
    // NOTE: Virtualizer's SharedmemoryMap already strips the base offset
    // before delivering the transaction to this slave socket, so `addr`
    // arrives as a register-relative offset (0x0 .. 0x1C). The original
    // line `addr -= BASE;` is removed: it was correct for standalone
    // testbenches (e.g. verifyDMA2 using TLM2Bus, which passes the full
    // system address through), but in Virtualizer it double-subtracts
    // and forces every access into the `default` (ADDRESS_ERROR) branch.
    if (cmd_r == tlm::TLM_WRITE_COMMAND) {
        // Pack raw payload bytes into a POD uint32 first. The original code
        // memcpy'd straight into &SOURCEx etc., but sc_uint<32> is NOT a POD:
        // it derives from sc_value_base (virtual), so the first 8 bytes are a
        // vtable pointer and the actual value m_val lives at a later offset.
        // Writing into the object's raw memory only clobbers the vtable area
        // and leaves m_val at 0, which is why dma_process never sees START!=0.
        unsigned int wval = 0;
        memcpy(&wval, r_data, r_len);
        std::cout << "DMA received WRITE at " << std::hex << "0x" << addr+BASE
                  << " length " << std::dec << r_len <<  ": ";
        switch (addr) {
            case 0x0:               // SOURCE0 register
                if (!block0) {
                    SOURCE0 = wval;
                    std::cout << std::hex << "0x" << SOURCE0 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0x4:               // TARGET0 register
                if (!block0) {
                    TARGET0 = wval;
                    std::cout << std::hex << "0x" << TARGET0 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0x8:              // SIZE0 register
                if (!block0) {
                    SIZE0 = wval;
                    std::cout << std::hex << "0x" << SIZE0 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0xC:             // START0/CLEAR0 register
                START0 = wval;
                std::cout << std::hex << "0x" << START0 << std::endl;
                if (START0 == 0x1)
                    block0 = true;  // Block from control register write
                else
                    block0 = false;
                break;
            case 0x10:            // SOURCE1 register
                if (!block1) {
                    SOURCE1 = wval;
                    std::cout << std::hex << "0x" << SOURCE1 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0x14:            // TARGET1 register
                if (!block1) {
                    TARGET1 = wval;
                    std::cout << std::hex << "0x" << TARGET1 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0x18:            // SIZE1 register
                if (!block1) {
                    SIZE1 = wval;
                    std::cout << std::hex << "0x" << SIZE1 << std::endl;
                } else {
                    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
                    std::cout << "blocked" << std::endl;
                }
                break;
            case 0x1C:           // START1/CLEAR1 register
                START1 = wval;
                std::cout << std::hex << "0x" << START1 << std::endl;
                if (START1 == 0x1)
                    block1 = true;  // Block from control register write
                else
                    block1 = false;
                break;
            default:
                trans.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
                std::cout << std::hex << "wrong address" << std::endl;
        }
    } else if (cmd_r == tlm::TLM_READ_COMMAND) {
        // Same sc_uint<32>-is-not-POD problem in reverse: pull the value via
        // proper conversion into a POD uint32, then memcpy that out.
        unsigned int rval = 0;
        switch (addr) {
            case 0x0:  rval = SOURCE0; break;
            case 0x4:  rval = TARGET0; break;
            case 0x8:  rval = SIZE0;   break;
            case 0xC:  rval = START0;  break;
            case 0x10: rval = SOURCE1; break;
            case 0x14: rval = TARGET1; break;
            case 0x18: rval = SIZE1;   break;
            case 0x1C: rval = START1;  break;
            default: break;
        }
        memcpy(r_data, &rval, r_len);
        std::cout << "DMA received READ at " << std::hex << "0x" << addr+BASE
                  << " length " << std::dec << r_len <<  ": "
                  << std::hex << "0x" << rval << std::endl;
    } else {               // TLM_IGNORE_COMMAND
        std::cout << "DMA receives TLM_IGNORE_COMMAND" << std::endl;
    }

    return;
}

void DMA2::dma_process0() {
    // Reset behavior
    SOURCE0 = 0;
    TARGET0 = 0;
    SIZE0 = 0;
    START0 = 0;
    block0 = false;
    intr0 = false;
    // INT0 follows the A35 PSP convention: nIRQ_<x> is active-LOW. Idle =
    // HIGH (de-asserted); on transfer complete we drive LOW. NB: the running
    // system synchronizes via polling, not IRQ — see main_cpu0.c. The
    // polarity is kept doc-compliant for code-review clarity.
    INT0.write(true);   // de-asserted (HIGH)

    // DMA operational loop
    while (true) {
        wait();

        unsigned int rwData0 = 0;
        // Start DMA transfer
        if (START0) {
            if (SIZE0 > 0) {
                // TLM transaction common parameters.
                // tlm_generic_payload's default streaming_width is 0, which
                // Virtualizer's SharedmemoryMap rejects with "transaction
                // streaming width is set to zero" → sim aborts. Set
                // streaming_width = data_length for a normal (non-streaming)
                // transfer per TLM-2.0 convention.
                trans0.set_data_ptr(trf_data0);
                unsigned int xfer_len = (SIZE0 >= 4) ? 4u : (unsigned int)SIZE0;
                trans0.set_data_length(xfer_len);
                trans0.set_streaming_width(xfer_len);

                //std::cout << "DMA SOURCE0 = " << std::hex << SOURCE0
                //        << " TARGET0 = " << std::hex << TARGET0 << std::endl;
                // TLM read transaction
                // trans0.set_command(tlm::TLM_READ_COMMAND);
                trans0.set_read();  // set TLM_READ_COMMAND
                trans0.set_address(SOURCE0);
                Msocket0->b_transport(trans0, delay);
                memcpy(&rwData0, trf_data0, 4);
                std::cout << "DMA0 read 0x" << std::hex << SOURCE0 << ":0x"
                          <<  rwData0 << std::endl;

                // Write to target
                // trans0.set_command(tlm::TLM_WRITE_COMMAND);
                trans0.set_write();  // set TLM_WRITE_COMMAND
                trans0.set_address(TARGET0);
                Msocket0->b_transport(trans0, delay);
                std::cout << "DMA0 write 0x" << std::hex << TARGET0 << ":0x"
                          <<  rwData0 << std::endl;

                if (SIZE0 > 4) {
                    SOURCE0 += 4;
                    TARGET0 += 4;
                    SIZE0 -= 4;
                } else
                    SIZE0 = 0;
                continue;
            }

            // Signal transfer is complete
            if (!intr0) {
                INT0.write(false);  // asserted (LOW) — fires ARM0.nIRQ_0
                intr0 = true;        // Interrupt pulled
                std::cout << "DMA INT0 sent" << std::endl;
            }
        } else {
            block0 = false;  // Resume control register write
            if (intr0) {
                INT0.write(true);   // de-asserted (HIGH)
                intr0 = false;   // Interrupt cleared
                std::cout << "DMA clears INT0" << std::endl;
            }
        }
    }
}


void DMA2::dma_process1() {
    // Reset behavior
    SOURCE1 = 0;
    TARGET1 = 0;
    SIZE1 = 0;
    START1 = 0;
    block1 = false;
    intr1 = false;
    // Same active-LOW convention as INT0 — wired to ARM0.nIRQ_1.
    INT1.write(true);   // de-asserted (HIGH)

    // DMA operational loop
    while (true) {
        wait();

        unsigned int rwData1 = 0;
        // Start DMA transfer
        if (START1) {
            if (SIZE1 > 0) {
                // TLM transaction common parameters.
                // See dma_process0 above for why streaming_width must be set.
                trans1.set_data_ptr(trf_data1);
                unsigned int xfer_len = (SIZE1 >= 4) ? 4u : (unsigned int)SIZE1;
                trans1.set_data_length(xfer_len);
                trans1.set_streaming_width(xfer_len);

                //std::cout << "DMA TARGET1 = " << std::hex << SOURCE
                //        << " TARGET1 = " << std::hex << TARGET0 << std::endl;
                // TLM read transaction
                // trans1.set_command(tlm::TLM_READ_COMMAND);
                trans1.set_read();  // set TLM_READ_COMMAND
                trans1.set_address(SOURCE1);
                Msocket1->b_transport(trans1, delay);
                memcpy(&rwData1, trf_data1, 4);
                std::cout << "DMA1 read 0x" << std::hex << SOURCE1 << ":0x"
                          <<  rwData1 << std::endl;

                // Write to target
                // trans1.set_command(tlm::TLM_WRITE_COMMAND);
                trans1.set_write();  // set TLM_WRITE_COMMAND
                trans1.set_address(TARGET1);
                Msocket1->b_transport(trans1, delay);
                std::cout << "DMA1 write 0x" << std::hex << TARGET1 << ":0x"
                          <<  rwData1 << std::endl;

                if (SIZE1 > 4) {
                    SOURCE1 += 4;
                    TARGET1 += 4;
                    SIZE1 -= 4;
                } else
                    SIZE1 = 0;
                continue;
            }

            // Signal transfer is complete
            if (!intr1) {
                INT1.write(false);  // asserted (LOW) — fires ARM0.nIRQ_1
                intr1 = true;        // Interrupt pulled
                std::cout << "DMA INT1 sent" << std::endl;
            }
        } else {
            block1 = false;  // Resume control register write
            if (intr1) {
                INT1.write(true);   // de-asserted (HIGH)
                intr1 = false;   // Interrupt cleared
                std::cout << "DMA clears INT1" << std::endl;
            }
        }
    }
}

