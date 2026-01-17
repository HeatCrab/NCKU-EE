#include "FuncReq_SPI_initiator.h"

FuncReq_SPI_initiator::FuncReq_SPI_initiator() {
 	 // Set parameter values here
}
void FuncReq_SPI_initiator::initialize() {
	 enable_logging();
	 this->rst_in.set_active_level(false);
	 this->rst_in.set_duration(sc_core::sc_time(100, SC_NS));
	 this->clk_in.set_period_ps(10000); // 10 NS (100 MHz)
	 this->spi_clk.set_period_ps(1000000); // 1 US (1 MHz)
}
void FuncReq_SPI_initiator::setup() {
	 this->Serial_IO.clear();
	 this->rst_in.do_reset_pulse();
	 this->Serial_IO.register_as_slave(2);
	 sc_core::sc_time bit_time = sc_core::sc_time(1000000, SC_PS);
	 this->Serial_IO.set_bit_time( bit_time );
}

void FuncReq_SPI_initiator::testInitiateInitiatorTransfer() {
 // Configure the SPICtrl registers and initiate a transfer
 this->bus_reg_in.write32(MCR, 0x00000041); // Configured as Master and strobe select
 this->bus_reg_in.write32(CTAR+0, 0x0000010F); // Frame size 16 bits, Preescaler 1
 this->bus_reg_in.write32(PUSHR, 0xAAAA0200); // CTAR 0, PCS 2, TXDATA 0xAAAA
 // Wait for the transfer to start
 if( this->Serial_IO.start_received_transfer_happened() == false) {
 sc_core::wait(this->Serial_IO.get_start_received_transfer_cb_event());
 }
 SCML2_ASSERT_THAT(true, "SPI transfer received");
 // get and check the received data
 unsigned int data = this->Serial_IO.get_data();
 SCML2_ASSERT_THAT((data == 0xAAAA), "SPI data received is correct");
 // Initiate the SPI response 
 this->Serial_IO.start_slave_transfer(0xBBBB, this->Serial_IO.get_length());
 // Wait for the transfer to end
 if( this->Serial_IO.end_received_transfer_happened() == false) {
 sc_core::wait(this->Serial_IO.get_end_received_transfer_cb_event());
 }
 SCML2_ASSERT_THAT(true, "SPI transfer completed");
 
 // check that the response is received correctly
 bool status;
 data = this->bus_reg_in.read32(POPR, &status);
 SCML2_ASSERT_THAT((data == 0xBBBB), "Response data is correct"); 
}