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
 * CHECKSUM:89e7412200954b383ee56baa533bacc853254aa9
 ***************************************************************************/
 
#include <TX_PATH.h>
#include <SPICtrl.h>


TX_PATHType::TX_PATHType(const scml2::base::object_name& name) : TX_PATHTypeBase(name)  {
  
}



bool TX_PATHType::_impl(unsigned int & value) {
  // FIXME: Default implementation. Implement this.
  typedef bool return_type;
  return return_type();
}
void TX_PATHType::push_impl(unsigned int value) {
	TXFIFO.push(value);
	if (TXFIFO.nr_elements > TXFIFO.almost_empty_level)
		TX_EMPTY = false;
}
bool TX_PATHType::pop_impl(unsigned int & value) {
	bool success = TXFIFO.pop(value);
	if (TXFIFO.nr_elements < TXFIFO.almost_full_level)
		TX_FULL = false;
	return success;
}
void TX_PATHType::handle_TXControl_main() {
  while(!TXFIFO.is_empty()) {
	unsigned int lastExtractedTxFifoItem;
	TXFIFO.pop(lastExtractedTxFifoItem);
	process_new_item(lastExtractedTxFifoItem);
  }
}
void TX_PATHType::handle_TXFIFO_new_item_available() {
  if (m_isDriver) {
	newItemEvent.notify(clk_period);
  }
}
void TX_PATHType::handle_TXFIFO_full() {
  TX_FULL = true;
}
void TX_PATHType::handle_TXFIFO_almost_full() {
  TX_FULL = true;
}
void TX_PATHType::handle_TXFIFO_empty() {
  TX_EMPTY = true;
}
void TX_PATHType::handle_TXFIFO_almost_empty() {
  TX_EMPTY = true;
}
