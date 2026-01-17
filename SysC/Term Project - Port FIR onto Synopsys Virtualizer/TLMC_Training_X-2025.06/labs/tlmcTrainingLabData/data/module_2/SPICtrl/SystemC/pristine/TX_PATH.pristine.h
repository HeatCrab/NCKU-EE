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
 * CHECKSUM:49d55efbe5d792bb307726cf0c69f4d9994cf61c
 ***************************************************************************/
 
#pragma once

#include <TX_PATHBase.h>


/**
 * \copydoc TX_PATHTypeBase
 */
class TX_PATHType : public TX_PATHTypeBase {
  public:
    SC_HAS_PROCESS(TX_PATHType);

    TX_PATHType(const scml2::base::object_name& name);

  private:
    virtual void handle_TXFIFO_new_item_available();
    virtual void handle_TXFIFO_full();
    virtual void handle_TXFIFO_almost_full();
    virtual void handle_TXFIFO_empty();
    virtual void handle_TXFIFO_almost_empty();
    virtual void handle_TXControl_main();
    virtual void push_impl(unsigned int value);
    virtual bool pop_impl(unsigned int & value);
    
  private:
        
};

