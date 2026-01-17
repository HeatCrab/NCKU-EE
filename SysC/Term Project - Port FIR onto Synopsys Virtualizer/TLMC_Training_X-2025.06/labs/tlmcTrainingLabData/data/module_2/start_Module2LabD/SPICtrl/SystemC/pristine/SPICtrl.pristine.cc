/***************************************************************************
 * Copyright 1996-2025 Synopsys, Inc.
 *
 * This Synopsys software and all associated documentation are proprietary
 * to Synopsys, Inc. and may only be used pursuant to the terms and
 * conditions of a written license agreement with Synopsys, Inc.
 * All other use, reproduction, modification, or distribution of the
 * Synopsys software or the associated documentation is strictly prohibited.
 ***************************************************************************/
 

/***************************************************************************
 * Generated snippet, used for detecting user edits.
 * CHECKSUM:bf6f6f77800252ec1ff8e7d70e76978ae81b4135
 ***************************************************************************/
 
#include "SPICtrl.h"


SPICtrl::SPICtrl(sc_core::sc_module_name name) : SPICtrlBase(name)  {
  
}

void SPICtrl::handle_TX_PATH_process_new_item(unsigned int value) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_CRC_MOD_main() {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_Serial_IO_protocol_engine_start_received_transfer_64bit_V3(unsigned long long data, unsigned bit_length, bool continuous_select) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_Serial_IO_protocol_engine_end_received_transfer() {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_rst_in_protocol_engine_reset_enter() {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_spi_clk_protocol_engine_period_updated(sc_core::sc_time period) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_post_write_MCR_MSTR_input_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_post_write_MCR_MSTR_driver_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_post_write_MCR_PCSSE_chip_select_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
}

void SPICtrl::handle_post_write_MCR_PCSSE_strobe_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
}

bool SPICtrl::handle_read_MCR_CLR_TXF(unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  value = this->MCR.CLR_TXF;
  return true;
}

bool SPICtrl::handle_write_MCR_CLR_TXF(const unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  this->MCR.CLR_TXF = value;
  return true;
}

bool SPICtrl::handle_read_MCR_CLR_RXF(unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  value = this->MCR.CLR_RXF;
  return true;
}

bool SPICtrl::handle_write_MCR_CLR_RXF(const unsigned int& value) {
  // FIXME: Default implementation. Implement this.
  this->MCR.CLR_RXF = value;
  return true;
}

scml2::access_restriction_result SPICtrl::restrict_PUSHR(unsigned int& data, unsigned int& bit_enables) {
  // FIXME: Default implementation. Implement this.
    return scml2::RESTRICT_NO_ERROR;
}

bool SPICtrl::handle_write_PUSHR(const unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
  this->PUSHR = ((this->PUSHR & ~byteEnables) | (value & byteEnables));
  return true;
}

bool SPICtrl::handle_read_POPR(unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) {
  // FIXME: Default implementation. Implement this.
  value = ((this->POPR & byteEnables) | (value & ~byteEnables));
  return true;
}

