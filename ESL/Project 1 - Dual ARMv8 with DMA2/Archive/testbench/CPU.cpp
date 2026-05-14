#include "CPU.h"

void CPU::startCPU() {
    int rst_count = 0;

    while (1) {
        wait();

        if (Reset.read()) {
            rst_count = 0;
            continue;
        } else if (clk.read()) {
            if (rst_count < 2) {
                rst_count++;
                continue;
            }

            // ── Handle interrupt_1 (ch0 done) ──
            if (interrupt_1.read() == 1) {
                data_start_0 = 0x0000;
                trans_m.set_command(tlm::TLM_WRITE_COMMAND);
                trans_m.set_data_length(4);
                trans_m.set_address(0x10000C);             // START_0
                trans_m.set_data_ptr(
                    (unsigned char*)&data_start_0);
                Msocket->b_transport(trans_m, delay);
                if (trans_m.is_response_error())
                    std::cerr << "Error clearing ch0" << std::endl;
                std::cout << "CPU received interrupt_1, ch0 cleared"
                          << std::endl;
            }

            // ── Handle interrupt_2 (ch1 done) ──
            if (interrupt_2.read() == 1) {
                data_start_1 = 0x0000;
                trans_m.set_command(tlm::TLM_WRITE_COMMAND);
                trans_m.set_data_length(4);
                trans_m.set_address(0x10001C);             // START_1
                trans_m.set_data_ptr(
                    (unsigned char*)&data_start_1);
                Msocket->b_transport(trans_m, delay);
                if (trans_m.is_response_error())
                    std::cerr << "Error clearing ch1" << std::endl;
                std::cout << "CPU received interrupt_2, ch1 cleared"
                          << std::endl;
            }

            // ── Program DMA2 ch0 if both interrupts are off ──
            if (interrupt_1.read() == 0 && interrupt_2.read() == 0) {
                // ch0: SOURCE=0x200000, TARGET=0x201000, SIZE=256
                data_source_0 = 0x200000;
                data_target_0 = 0x201000;
                data_size_0   = 256;
                data_start_0  = 0x0001;

                sc_dt::uint64 base0 = 0x100000;
                trans_m.set_data_length(4);
                trans_m.set_command(tlm::TLM_WRITE_COMMAND);

                trans_m.set_address(base0 + 0x00);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_source_0);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base0 + 0x04);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_target_0);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base0 + 0x08);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_size_0);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base0 + 0x0C);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_start_0);
                Msocket->b_transport(trans_m, delay);

                // ch1: SOURCE=0x300000, TARGET=0x301000, SIZE=256
                data_source_1 = 0x300000;
                data_target_1 = 0x301000;
                data_size_1   = 256;
                data_start_1  = 0x0001;

                sc_dt::uint64 base1 = 0x100010;
                trans_m.set_address(base1 + 0x00);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_source_1);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base1 + 0x04);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_target_1);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base1 + 0x08);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_size_1);
                Msocket->b_transport(trans_m, delay);
                wait(delay);

                trans_m.set_address(base1 + 0x0C);
                trans_m.set_data_ptr(
                    (unsigned char*)&data_start_1);
                Msocket->b_transport(trans_m, delay);

                std::cout << "CPU programmed DMA2 ch0 and ch1"
                          << std::endl;
            }
        }
    }
}
