#ifndef DMA2_H
#define DMA2_H

#include <systemc.h>
#include <tlm.h>
#include <tlm_utils/simple_target_socket.h>
#include <tlm_utils/simple_initiator_socket.h>

class DMA2: public sc_module {
public:
    // TLM sockets
    tlm_utils::simple_initiator_socket<DMA2> Msocket0;
    tlm_utils::simple_initiator_socket<DMA2> Msocket1;
    tlm_utils::simple_target_socket<DMA2>    Ssocket;

    // Other I/O ports
    sc_in<bool>  clk;            // Clock pin
    sc_out<bool> INT0;           // Interrupt pin 0
    sc_out<bool> INT1;           // Interrupt pin 1
    sc_in<bool>  RST;            // Reset pin

    sc_dt::uint64 BASE = 0x1000; // BASE address register

    // Control Registers
    sc_uint<32> SOURCE0;         // SOURCE0 register
    sc_uint<32> TARGET0;         // TARGET0 register
    sc_uint<32> SIZE0;           // SIZE0 register
    sc_uint<32> START0;          // START0/CLEAR0 register

    sc_uint<32> SOURCE1;         // SOURCE0 register
    sc_uint<32> TARGET1;         // TARGET0 register
    sc_uint<32> SIZE1;           // SIZE0 register
    sc_uint<32> START1;          // START0/CLEAR0 register

    // Data area
    tlm::tlm_generic_payload trans0, trans1;
    unsigned char trf_data0[4]; // Transfer data area, 4 bytes
    unsigned char trf_data1[4]; // Transfer data area, 4 bytes
    sc_time delay = sc_time(10, SC_NS);  // 10 ns transfer latency
    bool block0, block1, intr0, intr1;

    // Process function and TLM slave socket function
    void dma_process0();
    void dma_process1();
    void b_transport(tlm::tlm_generic_payload&, sc_time&);

    // DMA2 construction. The BASE address is hard coded.
    DMA2(sc_module_name name, sc_dt::uint64 base_)
        : Msocket0("Msocket0"), Msocket1("Msocket1"),
          Ssocket("Ssocket"), BASE(base_) {
        Ssocket.register_b_transport(this, &DMA2::b_transport);
        SC_CTHREAD(dma_process0, clk.pos());
        // System SYSRST is active-LOW (matches the ARM/UART nRESET
        // convention); see Parameters: active_level=false.
        reset_signal_is(RST, false);
        SC_CTHREAD(dma_process1, clk.pos());
        // Same active-LOW reset for the second channel's thread.
        reset_signal_is(RST, false);
    }
};
#endif
