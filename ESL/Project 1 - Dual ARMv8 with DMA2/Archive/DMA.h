#ifndef DMA_H
#define DMA_H

#include "systemc.h"
#include "tlm.h"
#include "tlm_utils/simple_initiator_socket.h"
#include "tlm_utils/simple_target_socket.h"

SC_MODULE(DMA) {

    // Clock and reset
    sc_in<bool> clk;
    sc_in<bool> reset;

    // Interrupt output ports (active high, Interrupt connectivity plane)
    sc_out<bool> interrupt_1;
    sc_out<bool> interrupt_2;

    // TLM sockets — one slave, two masters (one per channel)
    tlm_utils::simple_initiator_socket<DMA> master_0;
    tlm_utils::simple_initiator_socket<DMA> master_1;
    tlm_utils::simple_target_socket<DMA>    slave;

    // Control registers — channel 0 (ARMv8_0)
    sc_uint<32> SOURCE_0;
    sc_uint<32> TARGET_0;
    sc_uint<32> SIZE_0;
    sc_uint<32> START_0;   // Write 1 to start, write 0 to clear

    // Control registers — channel 1 (ARMv8_1)
    sc_uint<32> SOURCE_1;
    sc_uint<32> TARGET_1;
    sc_uint<32> SIZE_1;
    sc_uint<32> START_1;

    // Base address
    sc_dt::uint64 BASE;

    // Transfer state (one set per channel)
    bool block_0, intr_0;
    bool block_1, intr_1;

    // Transfer data areas and payloads (one per channel)
    tlm::tlm_generic_payload trans_0;
    tlm::tlm_generic_payload trans_1;
    unsigned char trf_data_0[4];
    unsigned char trf_data_1[4];
    sc_time delay;

    void thread_process_0();
    void thread_process_1();
    void b_transport(tlm::tlm_generic_payload& trans, sc_time& r_delay);

    SC_CTOR(DMA) : master_0("master_0"), master_1("master_1"), slave("slave"),
                   interrupt_1("interrupt_1"), interrupt_2("interrupt_2"),
                   SOURCE_0(0), TARGET_0(0), SIZE_0(0), START_0(0),
                   SOURCE_1(0), TARGET_1(0), SIZE_1(0), START_1(0),
                   BASE(0x100000),
                   block_0(false), intr_0(false),
                   block_1(false), intr_1(false),
                   delay(10, SC_NS) {
        slave.register_b_transport(this, &DMA::b_transport);

        SC_CTHREAD(thread_process_0, clk.pos());
        reset_signal_is(reset, true);

        SC_CTHREAD(thread_process_1, clk.pos());
        reset_signal_is(reset, true);
    }

};

#endif
