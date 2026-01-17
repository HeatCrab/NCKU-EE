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
 * CHECKSUM:fb3f0b5a730e0a25150b660147d637a200dcfeff
 ***************************************************************************/
 
#pragma once

#include <RX_PATHBase.h>


/**
 * \copydoc RX_PATHTypeBase
 */
class RX_PATHType : public RX_PATHTypeBase {
  public:
    SC_HAS_PROCESS(RX_PATHType);

    RX_PATHType(const scml2::base::object_name& name);

  private:
    virtual void handle_RXFIFO_full();
    virtual void handle_RXFIFO_almost_full();
    virtual bool pop_impl(unsigned int & value);
    virtual void push_impl(unsigned int value);
    
  private:
        
};

