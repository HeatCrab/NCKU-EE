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
 * CHECKSUM:62baebc542ea9459c522582ddcc326379007b889
 ***************************************************************************/
 
#include <RX_PATH.h>
#include <SPICtrl.h>


RX_PATHType::RX_PATHType(const scml2::base::object_name& name) : RX_PATHTypeBase(name)  {
  
}

void RX_PATHType::handle_RXFIFO_full() {
  RXF_FULL = true;
}

void RX_PATHType::push_impl(unsigned int value) {
	RXFIFO.push(value);
}

bool RX_PATHType::pop_impl(unsigned int & value) {
  bool result = RXFIFO.pop(value);
  RXF_FULL = false;
  if (RXFIFO.nr_elements < RXFIFO.almost_full_level)
  RXF_Overflow = false;
  return result;
}

void RX_PATHType::handle_RXFIFO_almost_full() {
  RXF_Overflow = true;
}
