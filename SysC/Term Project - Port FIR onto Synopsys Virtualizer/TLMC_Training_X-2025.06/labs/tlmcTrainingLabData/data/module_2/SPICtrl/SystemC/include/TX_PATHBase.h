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
 * CHECKSUM:43c826263a33a27d9d0abc256cd2731b6452b813
 ***************************************************************************/
 
 
 // Warning: This is an auto-generated file. All changes to this file will be overwritten.


#pragma once

#include <scml2.h>
#include <scml2_base.h>
#include "scml2_objects.h"





class SPICtrlBase;



class TX_PATHType;

#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif


class TX_PATHTypeBase : public scml2::base::object {
    typedef TX_PATHTypeBase ObjectBaseType;
  public:
    SC_HAS_PROCESS(TX_PATHTypeBase);

    TX_PATHTypeBase(const scml2::base::object_name& name) 
        : scml2::base::object(name)
        , push("push", this, &TX_PATHTypeBase::push_impl)
        , pop("pop", this, &TX_PATHTypeBase::pop_impl)
        , m_fifo_size("m_fifo_size")
        , UFL_TXF("UFL_TXF")
        , m_isDriver("m_isDriver")
        , TX_FULL("TX_FULL")
        , TX_EMPTY("TX_EMPTY")
        , clk_period("clk_period")
        , newItemEvent("newItemEvent")
        , TXFIFO("TXFIFO")
        , TXControl("TXControl") {
    }
    
    virtual ~TX_PATHTypeBase() {
      m_actions.clear();
    }
    
    virtual void reset_model() {
      reset_model_if_available(newItemEvent);
      reset_model_if_available(TXFIFO);
      reset_model_if_available(TXControl);
    }
  
    virtual void handle_TXFIFO_new_item_available() = 0;
    virtual void handle_TXFIFO_full() = 0;
    virtual void handle_TXFIFO_almost_full() = 0;
    virtual void handle_TXFIFO_empty() = 0;
    virtual void handle_TXFIFO_almost_empty() = 0;
    virtual void handle_TXControl_main() = 0;
    virtual void push_impl(unsigned int value) = 0;
    virtual bool pop_impl(unsigned int & value) = 0;

    SCML2_BASE_CALLBACK(process_new_item, void, unsigned int);
    scml2::base::behavior<void, unsigned int> push;
    scml2::base::behavior<bool, unsigned int &> pop;
    scml2::base::value_attribute<long long> m_fifo_size;
    scml2::base::value_attribute<unsigned long long> UFL_TXF;
    scml2::base::value_attribute<bool> m_isDriver;
    scml2::base::value_attribute<bool> TX_FULL;
    scml2::base::value_attribute<bool> TX_EMPTY;
    scml2::base::value_attribute<sc_core::sc_time> clk_period;
    scml2::objects::event newItemEvent;
    scml2::objects::fifo<unsigned int> TXFIFO;
    scml2::objects::process TXControl;
    scml2::base::actions m_actions;
    
    virtual void finalize_local_construction() {
        TXControl.advanced_options.systemc_events.resize(1);
        TXFIFO.version = scml2::objects::V2_0;
        TXFIFO.size = m_fifo_size;
        TXFIFO.almost_empty_level = UFL_TXF;
        m_actions.add_action("TXFIFO.almost_empty_level = UFL_TXF", [&](){TXFIFO.almost_empty_level = UFL_TXF;}, UFL_TXF);
        TXFIFO.almost_full_level = m_fifo_size-1;
        m_actions.add_action("TXFIFO.almost_full_level = m_fifo_size-1", [&](){TXFIFO.almost_full_level = m_fifo_size-1;}, m_fifo_size);
        TXFIFO.config_options.fifo_overflow_style = scml2::objects::OVERWRITE;
        TXFIFO.config_options.fifo_size_style = scml2::objects::MAX_SIZE;
        TXFIFO.set_new_item_available_callback(SCML2_CALLBACK(handle_TXFIFO_new_item_available));
        TXFIFO.set_full_callback(SCML2_CALLBACK(handle_TXFIFO_full));
        TXFIFO.set_almost_full_callback(SCML2_CALLBACK(handle_TXFIFO_almost_full));
        TXFIFO.set_empty_callback(SCML2_CALLBACK(handle_TXFIFO_empty));
        TXFIFO.set_almost_empty_callback(SCML2_CALLBACK(handle_TXFIFO_almost_empty));
        TXControl.type = scml2::objects::THREAD;
        /* TXControl.advanced_options.stack_size = ; */
        TXControl.advanced_options.systemc_events[0] = &newItemEvent;
        TXControl.set_main_callback(SCML2_CALLBACK(handle_TXControl_main));
		scml2::base::object::finalize_local_construction();
    }
private:
};
#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif


