#include "fakeCPU.h"

void fakeCPU::startCPU() {
    while(1) {
        wait();
        if (Reset.read()) {
            rst_count = 0;
            continue;
        } else if (clk.read()) {
            if (rst_count < 10) {
                rst_count++;
                continue;
            }
            if (Interrupt.read() == 1) {
                data_source = 0x0000;
                data_target = 0x0000;
                data_size = 0x0000;
                data_start = 0x0000;
                trans_m.set_command(tlm::TLM_WRITE_COMMAND);
                trans_m.set_write();
                trans_m.set_data_length(24);
                trans_m.set_data_ptr((unsigned char*)&data_start);
                if (zeroOne)
                    trans_m.set_address(0x10000c);
                else
                    trans_m.set_address(0x10001c);
                // Send transaction
                Msocket->b_transport(trans_m, delay);
                if (trans_m.is_response_error()) {
                    cerr << "Error in write transaction." << std::endl;
                }
                count = 0;
                std::cout << "CPU received Interrupt, CLEAR sent" << std::endl;
                while (Interrupt.read() == 1) {
                    std::cout << "CPU waits for Interrupt off" << std::endl;
                    wait(delay*4);
                }
                std::cout << "CPU receives Interrupt Cleared" << std::endl;
            } else if (Interrupt.read() == 0) {
                if (zeroOne) {
                    data_source = 0x200000;
                    data_target = 0x300100;
                } else {
                    data_source = 0x300000;
                    data_target = 0x200100;
                }
                data_size = 0x0012;
                data_start = 0x0001;

                while (count < 4) {
                    // Common TLM command settings
                    trans_m.set_command(tlm::TLM_WRITE_COMMAND);
                    trans_m.set_write();
                    trans_m.set_data_length(24);

                    if (count == 0){
                        if (zeroOne)
                            trans_m.set_address(0x100000);
                        else
                            trans_m.set_address(0x100010);
                        trans_m.set_data_ptr((unsigned char*)&data_source);
                    } else if (count == 1) {
                        if (zeroOne)
                            trans_m.set_address(0x100004);
                        else
                            trans_m.set_address(0x100014);
                        trans_m.set_data_ptr((unsigned char*)&data_target);
                    } else if (count == 2) {
                        if (zeroOne)
                            trans_m.set_address(0x100008);
                        else
                            trans_m.set_address(0x100018);
                        trans_m.set_data_ptr((unsigned char*)&data_size);
                    } else if (count == 3){
                        if (zeroOne)
                            trans_m.set_address(0x10000c);
                        else
                            trans_m.set_address(0x10001c);
                        trans_m.set_data_ptr((unsigned char*)&data_start);
                    }
                    // Send transaction
                    Msocket->b_transport(trans_m, delay);
                    if (trans_m.is_response_error()) {
                        if (zeroOne)
                            cerr << "CPU0 error in write transaction." << endl;
                        else
                            cerr << "CPU1 error in write transaction." << endl;
                    }
                    if (zeroOne)
                        cout << "CPU0 programs DMA" << endl;
                    else
                        cout << "CPU1 programs DMA" << endl;
                    wait(delay);
                    count++;
                }
                // Testing the blocking of register writes
                if (!errTest) {
                    trans_m.set_command(tlm::TLM_WRITE_COMMAND);
                    trans_m.set_write();
                    trans_m.set_data_length(24);
                    if (Tcount == 5 && zeroOne) {
                        trans_m.set_address(0x100010);
                        trans_m.set_data_ptr((unsigned char*)&data_source);
                        Msocket->b_transport(trans_m, delay);
                        if (trans_m.is_response_error()) {
                            cerr << "Error in write transaction." << std::endl;
                        }
                    } else if (Tcount == 10 && !zeroOne) {
                        trans_m.set_address(0x10000C);
                        data_start = 0x0000;
                        trans_m.set_data_ptr((unsigned char*)&data_start);
                        Msocket->b_transport(trans_m, delay);
                        if (trans_m.is_response_error()) {
                            cerr << "Error in write transaction." << std::endl;
                        }
                    } else if (Tcount == 40 && !zeroOne) {
                        trans_m.set_address(0x10000C);
                        data_start = 0x0001;
                        trans_m.set_data_ptr((unsigned char*)&data_start);
                        Msocket->b_transport(trans_m, delay);
                        if (trans_m.is_response_error()) {
                            cerr << "Error in write transaction." << std::endl;
                        }
                        errTest = true;
                    }
                    Tcount++;
                }
            }
        }
        //std::cout << "One DMA run is done" << endl;
    }
}
