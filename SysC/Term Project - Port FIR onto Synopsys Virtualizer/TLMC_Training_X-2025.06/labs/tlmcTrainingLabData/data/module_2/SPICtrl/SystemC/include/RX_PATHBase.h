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
 * CHECKSUM:8c93442e3f22583bb2636ece38f9ce2fe916c70f
 ***************************************************************************/
 
 
 // Warning: This is an auto-generated file. All changes to this file will be overwritten.


#pragma once

#include <scml2.h>
#include <scml2_base.h>
#include "scml2_objects.h"





class SPICtrlBase;



class RX_PATHType;

#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif


class RX_PATHTypeBase : public scml2::base::object {
    typedef RX_PATHTypeBase ObjectBaseType;
  public:
    SC_HAS_PROCESS(RX_PATHTypeBase);

    RX_PATHTypeBase(const scml2::base::object_name& name) 
        : scml2::base::object(name)
        , pop("pop", this, &RX_PATHTypeBase::pop_impl)
        , push("push", this, &RX_PATHTypeBase::push_impl)
        , m_fifo_size("m_fifo_size")
        , OFL_RXF("OFL_RXF")
        , RXF_FULL("RXF_FULL")
        , RXF_Overflow("RXF_Overflow")
        , RXFIFO("RXFIFO") {
    }
    
    virtual ~RX_PATHTypeBase() {
      m_actions.clear();
    }
    
    virtual void reset_model() {
      reset_model_if_available(RXFIFO);
    }
  
    virtual void handle_RXFIFO_full() = 0;
    virtual void handle_RXFIFO_almost_full() = 0;
    virtual bool pop_impl(unsigned int & value) = 0;
    virtual void push_impl(unsigned int value) = 0;

    scml2::base::behavior<bool, unsigned int &> pop;
    scml2::base::behavior<void, unsigned int> push;
    scml2::base::value_attribute<long long> m_fifo_size;
    scml2::base::value_attribute<unsigned long long> OFL_RXF;
    scml2::base::value_attribute<bool> RXF_FULL;
    scml2::base::value_attribute<bool> RXF_Overflow;
    scml2::objects::fifo<unsigned int> RXFIFO;
    scml2::base::actions m_actions;
    
    virtual void finalize_local_construction() {
        RXFIFO.version = scml2::objects::V2_0;
        RXFIFO.size = m_fifo_size;
        RXFIFO.almost_empty_level = 1;
        RXFIFO.almost_full_level = OFL_RXF;
        m_actions.add_action("RXFIFO.almost_full_level = OFL_RXF", [&](){RXFIFO.almost_full_level = OFL_RXF;}, OFL_RXF);
        RXFIFO.config_options.fifo_overflow_style = scml2::objects::OVERWRITE;
        RXFIFO.config_options.fifo_size_style = scml2::objects::MAX_SIZE;
        RXFIFO.set_full_callback(SCML2_CALLBACK(handle_RXFIFO_full));
        RXFIFO.set_almost_full_callback(SCML2_CALLBACK(handle_RXFIFO_almost_full));
		scml2::base::object::finalize_local_construction();
    }
private:
};
#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif


