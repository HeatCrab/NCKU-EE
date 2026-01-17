#include "FuncReq_SPI_target.h"

FuncReq_SPI_target::FuncReq_SPI_target() {
 this->target_id = 2;
}
void FuncReq_SPI_target::initialize() {
 enable_logging();
 this->rst_in.set_active_level(false);
 this->rst_in.set_duration(sc_core::sc_time(100, sc_core::SC_NS));
 this->clk_in.set_period_ps(10000); // 10 NS (100 MHz)
 this->spi_clk.set_period_ps(1000000); // 1 US (1 MHz)
}
void FuncReq_SPI_target::setup() {
 this->Serial_IO.clear();
 this->rst_in.do_reset_pulse();
 this->Serial_IO.register_as_master();
}

void FuncReq_SPI_target::testInitiateTargetTransfer() {
 // Configure the SPICtrl registers and store the response value
 this->bus_reg_in.write32(MCR, 0x00000040); // Configure as Slave and Strobe select
 this->bus_reg_in.write32(PUSHR, 0xCCCC); // Response data 0xCCCC
 // Initiate the SPI transfer (as master)
 this->Serial_IO.set_slave_select_type_strobe_select();
 sc_core::sc_time bit_time = sc_core::sc_time(1000000, SC_PS); // 1 US
 this->Serial_IO.set_bit_time( bit_time );
 this->Serial_IO.start_master_transfer(0xDDDD, 16, 2); // slave = 2
 // Wait for the response to start
 if( this->Serial_IO.start_received_transfer_happened() == false) {
 sc_core::wait(this->Serial_IO.get_start_received_transfer_cb_event());
 }
 // Check that the response data is correct
 unsigned int data = this->Serial_IO.get_data();
 SCML2_ASSERT_THAT((data == 0xCCCC), "SPI data received is correct");
 // Wait for the response to end (after delay = bit_time*16)
 if( this->Serial_IO.end_received_transfer_happened() == false) {
 sc_core::wait(this->Serial_IO.get_end_received_transfer_cb_event());
 }
 SCML2_ASSERT_THAT(true, "SPI transfer completed");
 // check time elapsed
 // check that the send data is received correctly
 bool status;
 data = this->bus_reg_in.read32(POPR, &status);
 SCML2_ASSERT_THAT((data == 0xDDDD), "SPI data is correct");
}
