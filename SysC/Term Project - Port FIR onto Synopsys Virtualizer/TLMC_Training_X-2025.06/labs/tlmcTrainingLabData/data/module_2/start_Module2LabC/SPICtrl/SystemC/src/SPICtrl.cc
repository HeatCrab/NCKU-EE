/***************************************************************************
 * Copyright 1996-2024 Synopsys, Inc.
 *
 * This Synopsys software and all associated documentation are proprietary
 * to Synopsys, Inc. and may only be used pursuant to the terms and
 * conditions of a written license agreement with Synopsys, Inc.
 * All other use, reproduction, modification, or distribution of the
 * Synopsys software or the associated documentation is strictly prohibited.
 ***************************************************************************/
 

/***************************************************************************
 * Generated snippet, used for detecting user edits.
 * CHECKSUM:0000000000000000000000000000000000000000
 ***************************************************************************/
 
#include "SPICtrl.h"


SPICtrl::SPICtrl(sc_core::sc_module_name name) : SPICtrlBase(name)  {
  
}

void SPICtrl::handle_Serial_IO_protocol_engine_start_received_transfer_64bit_V3(unsigned long long data, unsigned bit_length, bool continuous_select) {
	this->SHIFT_REGISTER = data;
	if (this->Serial_IO_protocol_engine.getIsSlave()) {
	unsigned int value;
	if (TX_PATH.pop(value) == false) {
	SCML2_ERROR(BUFFER_UNDERFLOW) <<
	"Transmit Fifo is empty, transferring unknown data" << endl;
	    }
		Serial_IO_protocol_engine.start_slave_transfer(value, bit_length);
	}
}

void SPICtrl::handle_Serial_IO_protocol_engine_end_received_transfer() {
  RX_PATH.push(SHIFT_REGISTER);
}

void SPICtrl::handle_rst_in_protocol_engine_reset_enter() {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_spi_clk_protocol_engine_period_updated(sc_core::sc_time period) {
  this->Serial_IO_protocol_engine.bit_time = period;
}

void SPICtrl::handle_TX_PATH_process_new_item(unsigned int value) {
	unsigned int iCtar = (value >> 1) & 0x7; // extract transfer configuration index
	unsigned int PCS = (value >> 8) & 0xFF; // get peripheral chip select
	unsigned int TXDATA = (value >> 16) & 0xFFFF; // get transfer data
	unsigned int pre = this->CTAR[iCtar].PCSSCK; // get clock prescaler for this configuration
	unsigned int nBits = this->CTAR[iCtar].FMSZ + 1; // get framesize for this configuration
	// start transfer on Serial_IO
	this->Serial_IO_protocol_engine.bit_time = this->spi_clk_protocol_engine.period / pre;
	this->Serial_IO_protocol_engine.start_master_transfer(TXDATA, nBits, PCS);
	this->SR.TCF = 1; // set transfer complete bit
	this->SHIFT_REGISTER = TXDATA; // copy transmit data to shift register
}
bool SPICtrl::handle_write_MCR_CLR_TXF(const unsigned int& value) {
	this->MCR.CLR_TXF = value;
	if (value == 1) this->TX_PATH.TXFIFO.clear();
	return true;
}
bool SPICtrl::handle_read_MCR_CLR_TXF(unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  value = 0;
  return true;
}
bool SPICtrl::handle_write_PUSHR(const unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) {
  this->PUSHR = ((this->PUSHR & ~byteEnables) | (value & byteEnables));
  this->TX_PATH.push( (unsigned int) this->PUSHR);
  return true;
}
scml2::access_restriction_result SPICtrl::restrict_PUSHR(unsigned int& data, unsigned int& bit_enables) {
  if (this->MCR.MDIS == 1) {
	SCML2_WARNING(PROGRAMMING_WARNING) <<
	"Pushing data to the TX FIFO while controller is disabled" << endl;
	scml2::restrict_all(data, bit_enables);
  }
  return scml2::RESTRICT_NO_ERROR;
}
bool SPICtrl::handle_read_MCR_CLR_RXF(unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  value = 0;
  return true;
}
bool SPICtrl::handle_write_MCR_CLR_RXF(const unsigned int& value) {
  this->MCR.CLR_RXF = value;
  if (value == 1) this->RX_PATH.RXFIFO.clear();
  return true;
}
bool SPICtrl::handle_read_POPR(unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) {
  unsigned int tempData = 0;
  this->RX_PATH.pop(tempData);
  this->POPR = tempData;
  value = ((this->POPR & byteEnables) | (value & ~byteEnables));
  return true;
}
void SPICtrl::handle_post_write_MCR_MSTR_input_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  SCML2_INFO(FUNCTIONAL_LOG) << "Controller configured as Target." << std::endl;
  this->Serial_IO_protocol_engine.register_as_slave(target_id);
}
void SPICtrl::handle_post_write_MCR_MSTR_driver_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  SCML2_INFO(FUNCTIONAL_LOG) << "Controller configured as Initiator." << std::endl;
  this->Serial_IO_protocol_engine.register_as_master();
}
void SPICtrl::handle_post_write_MCR_PCSSE_chip_select_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  this->Serial_IO_protocol_engine.set_slave_select_type_chip_select();
}
void SPICtrl::handle_post_write_MCR_PCSSE_strobe_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  this-> Serial_IO_protocol_engine.set_slave_select_type_strobe_select();
}
