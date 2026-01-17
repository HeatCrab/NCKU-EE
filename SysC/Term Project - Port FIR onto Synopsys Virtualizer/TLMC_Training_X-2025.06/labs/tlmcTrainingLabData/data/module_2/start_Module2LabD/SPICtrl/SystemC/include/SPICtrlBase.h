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
 * CHECKSUM:e05cd102664945c826632493d3f791f5e7d855e1
 ***************************************************************************/
 

 
 // Warning: This is an auto-generated file. All changes to this file will be overwritten.


#pragma once

#include <systemc>
#include <scmlinc/scml_property.h>
#include "scml2_objects.h"
#include <TX_PATH.h>
#include <RX_PATH.h>
#include <scml2_base.h>
#include "scml2_protocol_engines/tlm2_ft_target_port/include/tlm2_ft_target_port_pe.h"
#include "tlm_ft_spi_device_socket.h"
#include "tlm_ft_spi_protocol_engine.h"
#include "scml2_protocol_engines/reset/include/reset_engine.h"
#include "scml2_protocol_engines/clock/include/clock_engine.h"
#include "scml2_protocol_engines/interrupt/include/interrupt_engine.h"
#include <scml2.h>




class SPICtrlCovermodelBase;


class SPICtrlCovermodel;


class SPICtrl;

/**
 * Serial Protocol Interface (SPI) controller peripheral
 * 
 * \author Synopsys
 * \version 1.0
 */
#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif


class SPICtrlBase : public sc_core::sc_module {
    typedef SPICtrlBase ModelBaseType;
  public:
    SC_HAS_PROCESS(SPICtrlBase);

    SPICtrlBase(sc_core::sc_module_name name) 
        : sc_core::sc_module(name)
        , enable_check_clocks("enable_check_clocks", false)
        , target_id("target_id", 0)
        , fifo_size("fifo_size", 5)
        , version("version", 10003)
        , bus_reg_in("bus_reg_in")
        , Serial_IO("Serial_IO")
        , rst_in("rst_in")
        , spi_clk("spi_clk")
        , clk_in("clk_in")
        , tfuf_irq("tfuf_irq")
        , tfff_irq("tfff_irq")
        , rfof_irq("rfof_irq")
        , rfdf_irq("rfdf_irq")
        , bus_reg_in_router("bus_reg_in_router")
        , TX_PATH("TX_PATH")
        , RX_PATH("RX_PATH")
        , SHIFT_REGISTER("SHIFT_REGISTER")
        , CRC_MOD("CRC_MOD")
        , bus_reg_in_protocol_engine("bus_reg_in_protocol_engine", bus_reg_in)
        , Serial_IO_protocol_engine("Serial_IO_protocol_engine", Serial_IO)
        , rst_in_protocol_engine("rst_in_protocol_engine", rst_in)
        , spi_clk_protocol_engine("spi_clk_protocol_engine", spi_clk)
        , clk_in_protocol_engine("clk_in_protocol_engine", clk_in)
        , tfuf_irq_protocol_engine("tfuf_irq_protocol_engine", tfuf_irq)
        , tfff_irq_protocol_engine("tfff_irq_protocol_engine", tfff_irq)
        , rfof_irq_protocol_engine("rfof_irq_protocol_engine", rfof_irq)
        , rfdf_irq_protocol_engine("rfdf_irq_protocol_engine", rfdf_irq)
        , mRegs("mRegs", (0x24) / scml2::sizeOf<unsigned int >())
        , MCR(sc_core::sc_gen_unique_name("MCR", true), mRegs, (0x0) / scml2::sizeOf<unsigned int >())
        , MCR_reset_value(0)
        , MCR_reset_mask(4294967295)
        , CTAR("CTAR", 4, scml2::create_reg_vector_creator< unsigned int, CTAR_type >(mRegs, (0x4) / scml2::sizeOf<unsigned int >(), 1))
        , CTAR_reset_value(0)
        , CTAR_reset_mask(4294967295)
        , SR(sc_core::sc_gen_unique_name("SR", true), mRegs, (0x14) / scml2::sizeOf<unsigned int >(), *this)
        , SR_reset_value(0)
        , SR_reset_mask(4294967295)
        , RSER(sc_core::sc_gen_unique_name("RSER", true), mRegs, (0x18) / scml2::sizeOf<unsigned int >())
        , RSER_reset_value(0x0)
        , PUSHR(sc_core::sc_gen_unique_name("PUSHR", true), mRegs, (0x1c) / scml2::sizeOf<unsigned int >())
        , PUSHR_reset_value(0x0)
        , POPR(sc_core::sc_gen_unique_name("POPR", true), mRegs, (0x20) / scml2::sizeOf<unsigned int >())
        , POPR_reset_value(0x0) {
      bus_reg_in_router.mappings.resize(1);
      bus_reg_in_protocol_engine.intercepts.resize(0);
      bus_reg_in_router.bound_on = bus_reg_in_protocol_engine;
      bus_reg_in_router.mappings[0].base = 0x0;
      bus_reg_in_router.mappings[0].size = mRegs.get_size()*mRegs.get_width();
      bus_reg_in_router.mappings[0].destination = mRegs;
      /* bus_reg_in_router.mappings[0].offset = ; */
      bus_reg_in_router.mappings[0].type = scml2::objects::RW;
      bus_reg_in_router.mappings[0].active = true;
      /* bus_reg_in_router.mappings[0].name = ; */
      bus_reg_in_router.finalize_construction();
      TX_PATH.m_fifo_size = fifo_size;
      TX_PATH.UFL_TXF = MCR.UFL_TXF;
      m_actions.add_action("TX_PATH.UFL_TXF = MCR.UFL_TXF", [&](){TX_PATH.UFL_TXF = MCR.UFL_TXF;}, MCR.UFL_TXF);
      TX_PATH.m_isDriver = (MCR.MSTR == 1);
      m_actions.add_action("TX_PATH.m_isDriver = (MCR.MSTR == 1)", [&](){TX_PATH.m_isDriver = (MCR.MSTR == 1);}, MCR.MSTR);
      TX_PATH.TX_FULL = false;
      TX_PATH.TX_EMPTY = false;
      TX_PATH.clk_period = clk_in_protocol_engine.period;
      m_actions.add_action("TX_PATH.clk_period = clk_in_protocol_engine.period", [&](){TX_PATH.clk_period = clk_in_protocol_engine.period;}, clk_in_protocol_engine.period);
      TX_PATH.set_process_new_item_callback(SCML2_CALLBACK(handle_TX_PATH_process_new_item));
      TX_PATH.finalize_construction();
      RX_PATH.m_fifo_size = fifo_size;
      RX_PATH.OFL_RXF = MCR.OFL_RXF;
      m_actions.add_action("RX_PATH.OFL_RXF = MCR.OFL_RXF", [&](){RX_PATH.OFL_RXF = MCR.OFL_RXF;}, MCR.OFL_RXF);
      RX_PATH.RXF_FULL = false;
      RX_PATH.RXF_Overflow = false;
      RX_PATH.finalize_construction();
      SHIFT_REGISTER.value = 0;
      SHIFT_REGISTER.advanced_options.analysis_on = false;
      SHIFT_REGISTER.advanced_options.analysis_name = "scml_variable_trace";
      SHIFT_REGISTER.advanced_options.command_enabled = false;
      /* SHIFT_REGISTER.advanced_options.command_name = ; */
      SHIFT_REGISTER.finalize_construction();
      CRC_MOD.set_main_callback(SCML2_CALLBACK(handle_CRC_MOD_main));
      CRC_MOD.finalize_construction();
      bus_reg_in_protocol_engine.abstraction = scml2::LT;
      bus_reg_in_protocol_engine.consume_annotated_time = false;
      bus_reg_in_protocol_engine.finalize_construction();
      Serial_IO_protocol_engine.version = V3_0;
      Serial_IO_protocol_engine.bit_time = sc_core::sc_time(1, SC_US);
      Serial_IO_protocol_engine.check_clocks = enable_check_clocks;
      Serial_IO_protocol_engine.set_start_received_transfer_64bit_V3_callback(SCML2_CALLBACK(handle_Serial_IO_protocol_engine_start_received_transfer_64bit_V3));
      Serial_IO_protocol_engine.set_end_received_transfer_callback(SCML2_CALLBACK(handle_Serial_IO_protocol_engine_end_received_transfer));
      Serial_IO_protocol_engine.finalize_construction();
      rst_in_protocol_engine.active_level = false;
      rst_in_protocol_engine.set_reset_enter_callback(SCML2_CALLBACK(handle_rst_in_protocol_engine_reset_enter));
      rst_in_protocol_engine.finalize_construction();
      spi_clk_protocol_engine.divider = 1;
      /* spi_clk_protocol_engine.enabled = ; */
      spi_clk_protocol_engine.set_period_updated_callback(SCML2_CALLBACK(handle_spi_clk_protocol_engine_period_updated));
      spi_clk_protocol_engine.finalize_construction();
      clk_in_protocol_engine.divider = 1;
      /* clk_in_protocol_engine.enabled = ; */
      clk_in_protocol_engine.finalize_construction();
      tfuf_irq_protocol_engine.active_level = false;
      tfuf_irq_protocol_engine.enable = (SR.TFUF == 1);
      m_actions.add_action("tfuf_irq_protocol_engine.enable = (SR.TFUF == 1)", [&](){tfuf_irq_protocol_engine.enable = (SR.TFUF == 1);}, SR.TFUF);
      tfuf_irq_protocol_engine.finalize_construction();
      tfff_irq_protocol_engine.active_level = false;
      tfff_irq_protocol_engine.enable = (SR.TFFF == 1);
      m_actions.add_action("tfff_irq_protocol_engine.enable = (SR.TFFF == 1)", [&](){tfff_irq_protocol_engine.enable = (SR.TFFF == 1);}, SR.TFFF);
      tfff_irq_protocol_engine.finalize_construction();
      rfof_irq_protocol_engine.active_level = false;
      rfof_irq_protocol_engine.enable = (SR.RFOF == 1);
      m_actions.add_action("rfof_irq_protocol_engine.enable = (SR.RFOF == 1)", [&](){rfof_irq_protocol_engine.enable = (SR.RFOF == 1);}, SR.RFOF);
      rfof_irq_protocol_engine.finalize_construction();
      rfdf_irq_protocol_engine.active_level = false;
      rfdf_irq_protocol_engine.enable = (SR.RFDF == 1);
      m_actions.add_action("rfdf_irq_protocol_engine.enable = (SR.RFDF == 1)", [&](){rfdf_irq_protocol_engine.enable = (SR.RFDF == 1);}, SR.RFDF);
      rfdf_irq_protocol_engine.finalize_construction();
      scml2::set_ignore_restriction<unsigned int, scml2::reg>(MCR, (unsigned int)0ull, (unsigned int)4291625150ull);
      MCR.MSTR.set_symbolic_name(MCR.MSTR.input_mode, "input_mode");
      scml2::set_post_write_callback(MCR.MSTR, MCR.MSTR.input_mode, SCML2_CALLBACK(handle_post_write_MCR_MSTR_input_mode));
      MCR.MSTR.set_symbolic_name(MCR.MSTR.driver_mode, "driver_mode");
      scml2::set_post_write_callback(MCR.MSTR, MCR.MSTR.driver_mode, SCML2_CALLBACK(handle_post_write_MCR_MSTR_driver_mode));
      MCR.PCSSE.set_symbolic_name(MCR.PCSSE.chip_select_mode, "chip_select_mode");
      scml2::set_post_write_callback(MCR.PCSSE, MCR.PCSSE.chip_select_mode, SCML2_CALLBACK(handle_post_write_MCR_PCSSE_chip_select_mode));
      MCR.PCSSE.set_symbolic_name(MCR.PCSSE.strobe_mode, "strobe_mode");
      scml2::set_post_write_callback(MCR.PCSSE, MCR.PCSSE.strobe_mode, SCML2_CALLBACK(handle_post_write_MCR_PCSSE_strobe_mode));
      scml2::set_read_no_store_callback(MCR.CLR_TXF, SCML2_CALLBACK(handle_read_MCR_CLR_TXF), scml2::AUTO_SYNCING);
      scml2::set_write_callback(MCR.CLR_TXF, SCML2_CALLBACK(handle_write_MCR_CLR_TXF), scml2::AUTO_SYNCING);
      scml2::set_read_no_store_callback(MCR.CLR_RXF, SCML2_CALLBACK(handle_read_MCR_CLR_RXF), scml2::AUTO_SYNCING);
      scml2::set_write_callback(MCR.CLR_RXF, SCML2_CALLBACK(handle_write_MCR_CLR_RXF), scml2::AUTO_SYNCING);
      for (size_t CTAR_i = 0; CTAR_i < 4; ++CTAR_i) {
        scml2::set_ignore_restriction<unsigned int, scml2::reg>(CTAR[CTAR_i], (unsigned int)0ull, (unsigned int)4294966272ull);
      }
      scml2::set_ignore_restriction<unsigned int, scml2::reg>(SR, (unsigned int)0ull, (unsigned int)12196ull);
      scml2::set_clear_on_write_1(SR.TCF);
      scml2::set_clear_on_write_1(SR.TXRXS);
      scml2::set_clear_on_write_1(SR.EOQF);
      scml2::set_clear_on_write_1(SR.TFUF);
      SR.TFUF = (TX_PATH.TX_EMPTY) ? 1 : 0;
      m_actions.add_action("SR.TFUF = (TX_PATH.TX_EMPTY) ? 1 : 0", [&](){SR.TFUF = (TX_PATH.TX_EMPTY) ? 1 : 0;}, TX_PATH.TX_EMPTY);
      scml2::set_clear_on_write_1(SR.TFFF);
      SR.TFFF = (TX_PATH.TX_FULL) ? 1 : 0;
      m_actions.add_action("SR.TFFF = (TX_PATH.TX_FULL) ? 1 : 0", [&](){SR.TFFF = (TX_PATH.TX_FULL) ? 1 : 0;}, TX_PATH.TX_FULL);
      scml2::set_clear_on_write_1(SR.RFOF);
      SR.RFOF = (RX_PATH.RXF_FULL) ? 1 : 0;
      m_actions.add_action("SR.RFOF = (RX_PATH.RXF_FULL) ? 1 : 0", [&](){SR.RFOF = (RX_PATH.RXF_FULL) ? 1 : 0;}, RX_PATH.RXF_FULL);
      scml2::set_clear_on_write_1(SR.RFDF);
      SR.RFDF = (RX_PATH.RXF_Overflow) ? 1 : 0;
      m_actions.add_action("SR.RFDF = (RX_PATH.RXF_Overflow) ? 1 : 0", [&](){SR.RFDF = (RX_PATH.RXF_Overflow) ? 1 : 0;}, RX_PATH.RXF_Overflow);
      if (version < 10200) {
        scml2::set_ignore_restriction((scml2::bitfield<unsigned int>&)SR.reserved4);
      }
      scml2::set_write_restriction<unsigned int, scml2::reg>(PUSHR, SCML2_CALLBACK(restrict_PUSHR));
      scml2::set_write_callback<unsigned int, scml2::reg>(PUSHR, SCML2_CALLBACK(handle_write_PUSHR), scml2::AUTO_SYNCING);
      scml2::set_write_ignore_restriction<unsigned int, scml2::reg>(POPR);
      scml2::set_read_no_store_callback<unsigned int, scml2::reg>(POPR, SCML2_CALLBACK(handle_read_POPR), scml2::AUTO_SYNCING);
    }
    
// LCOV_EXCL_START
    virtual ~SPICtrlBase() {
      m_actions.clear();
    }
// LCOV_EXCL_STOP    

  protected:
    /**
     * This method resets all interfaces, registers, and bitfields to their reset value.
     * It is typically called from end_of_elaboration(), and connected to the reset port.
     */
    
    virtual void reset_model() {
      reset_model_if_available(bus_reg_in_router);
      reset_model_if_available(TX_PATH);
      reset_model_if_available(RX_PATH);
      reset_model_if_available(SHIFT_REGISTER);
      reset_model_if_available(CRC_MOD);
      MCR = (MCR & ~MCR_reset_mask) | (MCR_reset_value & MCR_reset_mask);
      for (size_t CTAR_i = 0; CTAR_i < 4; ++CTAR_i) {
        CTAR[CTAR_i] = (CTAR[CTAR_i] & ~CTAR_reset_mask) | (CTAR_reset_value & CTAR_reset_mask);
      }
      SR = (SR & ~SR_reset_mask) | (SR_reset_value & SR_reset_mask);
      RSER = RSER_reset_value;
      PUSHR = PUSHR_reset_value;
      POPR = POPR_reset_value;
    }
    
    virtual void end_of_elaboration() {
      sc_core::sc_module::end_of_elaboration();
      reset_model();
    }
    
    ModelBaseType& model() {
      return *this;
    }
    
    virtual void handle_post_write_MCR_MSTR_input_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) = 0;
    
    virtual void handle_post_write_MCR_MSTR_driver_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) = 0;
    
    virtual void handle_post_write_MCR_PCSSE_chip_select_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) = 0;
    
    virtual void handle_post_write_MCR_PCSSE_strobe_mode(const unsigned int& old_value, const unsigned int& value, sc_core::sc_time& time) = 0;
  
    virtual void handle_TX_PATH_process_new_item(unsigned int value) = 0;
    virtual void handle_CRC_MOD_main() = 0;
    virtual void handle_Serial_IO_protocol_engine_start_received_transfer_64bit_V3(unsigned long long data, unsigned bit_length, bool continuous_select) = 0;
    virtual void handle_Serial_IO_protocol_engine_end_received_transfer() = 0;
    virtual void handle_rst_in_protocol_engine_reset_enter() = 0;
    virtual void handle_spi_clk_protocol_engine_period_updated(sc_core::sc_time period) = 0;
    virtual bool handle_read_MCR_CLR_TXF(unsigned int& value) = 0;
    virtual bool handle_write_MCR_CLR_TXF(const unsigned int& value) = 0;
    virtual bool handle_read_MCR_CLR_RXF(unsigned int& value) = 0;
    virtual bool handle_write_MCR_CLR_RXF(const unsigned int& value) = 0;
    virtual scml2::access_restriction_result restrict_PUSHR(unsigned int& data, unsigned int& bit_enables) = 0;
    virtual bool handle_write_PUSHR(const unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) = 0;
    virtual bool handle_read_POPR(unsigned int& value, const unsigned int& byteEnables, sc_core::sc_time& time) = 0;

  protected:
    /* Enable/disable the check on the SPI clock communication */
    scml_property<bool> enable_check_clocks;
    /* Identify SPI when in input mode */
    scml_property<unsigned int> target_id;
    /* Size of the internal FIFOs */
    scml_property<unsigned int> fifo_size;
    scml_property<int> version;

  public:
    scml2::ft_target_socket<32> bus_reg_in;
    tlm_ft_spi_device_socket Serial_IO;
    sc_core::sc_in<bool> rst_in;
    sc_core::sc_in<bool> spi_clk;
    sc_core::sc_in<bool> clk_in;
    sc_core::sc_out<bool> tfuf_irq;
    sc_core::sc_out<bool> tfff_irq;
    sc_core::sc_out<bool> rfof_irq;
    sc_core::sc_out<bool> rfdf_irq;

  protected:
    friend class SPICtrlCovermodelBase;
    friend class SPICtrlCovermodel;
    friend class SPICtrl;
    friend class TX_PATHType;
    friend class TX_PATHTypeBase;
    friend class RX_PATHType;
    friend class RX_PATHTypeBase;

    struct MCR_type : public scml2::reg< unsigned int > {
      ~MCR_type();
      MCR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset);
      using scml2::reg< unsigned int >::operator=;
      using scml2::reg< unsigned int >::operator+=;
      using scml2::reg< unsigned int >::operator-=;
      using scml2::reg< unsigned int >::operator/=;
      using scml2::reg< unsigned int >::operator*=;
      using scml2::reg< unsigned int >::operator%=;
      using scml2::reg< unsigned int >::operator^=;
      using scml2::reg< unsigned int >::operator&=;
      using scml2::reg< unsigned int >::operator|=;
      using scml2::reg< unsigned int >::operator>>=;
      using scml2::reg< unsigned int >::operator<<=;
      using scml2::reg< unsigned int >::operator--;
      using scml2::reg< unsigned int >::operator++;
      using scml2::reg< unsigned int >::operator unsigned int;
      struct MCR_MSTR_type : public scml2::bitfield< unsigned int > {
        ~MCR_MSTR_type();
        MCR_MSTR_type(const std::string& name, scml2::reg< unsigned int >& parent, unsigned int offset, unsigned int size);
        using scml2::bitfield< unsigned int >::operator=;
        using scml2::bitfield< unsigned int >::operator+=;
        using scml2::bitfield< unsigned int >::operator-=;
        using scml2::bitfield< unsigned int >::operator/=;
        using scml2::bitfield< unsigned int >::operator*=;
        using scml2::bitfield< unsigned int >::operator%=;
        using scml2::bitfield< unsigned int >::operator^=;
        using scml2::bitfield< unsigned int >::operator&=;
        using scml2::bitfield< unsigned int >::operator|=;
        using scml2::bitfield< unsigned int >::operator>>=;
        using scml2::bitfield< unsigned int >::operator<<=;
        using scml2::bitfield< unsigned int >::operator--;
        using scml2::bitfield< unsigned int >::operator++;
        using scml2::bitfield< unsigned int >::operator unsigned int;
        void put_input_mode() {
              put(input_mode);
        }
        bool is_input_mode() {
              return (input_mode== get());
        }
        void put_driver_mode() {
              put(driver_mode);
        }
        bool is_driver_mode() {
              return (driver_mode== get());
        }
        enum Enums {
          input_mode = 0,
          driver_mode = 1,
        };
      };
      struct MCR_PCSSE_type : public scml2::bitfield< unsigned int > {
        ~MCR_PCSSE_type();
        MCR_PCSSE_type(const std::string& name, scml2::reg< unsigned int >& parent, unsigned int offset, unsigned int size);
        using scml2::bitfield< unsigned int >::operator=;
        using scml2::bitfield< unsigned int >::operator+=;
        using scml2::bitfield< unsigned int >::operator-=;
        using scml2::bitfield< unsigned int >::operator/=;
        using scml2::bitfield< unsigned int >::operator*=;
        using scml2::bitfield< unsigned int >::operator%=;
        using scml2::bitfield< unsigned int >::operator^=;
        using scml2::bitfield< unsigned int >::operator&=;
        using scml2::bitfield< unsigned int >::operator|=;
        using scml2::bitfield< unsigned int >::operator>>=;
        using scml2::bitfield< unsigned int >::operator<<=;
        using scml2::bitfield< unsigned int >::operator--;
        using scml2::bitfield< unsigned int >::operator++;
        using scml2::bitfield< unsigned int >::operator unsigned int;
        void put_chip_select_mode() {
              put(chip_select_mode);
        }
        bool is_chip_select_mode() {
              return (chip_select_mode== get());
        }
        void put_strobe_mode() {
              put(strobe_mode);
        }
        bool is_strobe_mode() {
              return (strobe_mode== get());
        }
        enum Enums {
          chip_select_mode = 0,
          strobe_mode = 1,
        };
      };
      /* Bit to configure the SPI in either Initiator (value 1) or Target mode (value 0) */
      MCR_MSTR_type MSTR;
      /* Bit to enable the Peripheral Chip Select in Strobe mode (value 1) */
      MCR_PCSSE_type PCSSE;
      /* Bitfield to set the Underflow alarm level of the Transmit Fifo */
      scml2::bitfield< unsigned int > UFL_TXF;
      /* Bitfield to set the Overflow alarm level of the Receive Fifo */
      scml2::bitfield< unsigned int > OFL_RXF;
      /* Bit to disable the module */
      scml2::bitfield< unsigned int > MDIS;
      /* Bit to clear/flush the TX FIFO */
      scml2::bitfield< unsigned int > CLR_TXF;
      /* Bit to clear/flush the RX FIFO */
      scml2::bitfield< unsigned int > CLR_RXF;
    };
    struct CTAR_type : public scml2::reg< unsigned int > {
      ~CTAR_type();
      CTAR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset);
      using scml2::reg< unsigned int >::operator=;
      using scml2::reg< unsigned int >::operator+=;
      using scml2::reg< unsigned int >::operator-=;
      using scml2::reg< unsigned int >::operator/=;
      using scml2::reg< unsigned int >::operator*=;
      using scml2::reg< unsigned int >::operator%=;
      using scml2::reg< unsigned int >::operator^=;
      using scml2::reg< unsigned int >::operator&=;
      using scml2::reg< unsigned int >::operator|=;
      using scml2::reg< unsigned int >::operator>>=;
      using scml2::reg< unsigned int >::operator<<=;
      using scml2::reg< unsigned int >::operator--;
      using scml2::reg< unsigned int >::operator++;
      using scml2::reg< unsigned int >::operator unsigned int;
      /* Bit to configure the Frame Size (bits transferred equals this value plus 1) */
      scml2::bitfield< unsigned int > FMSZ;
      /* Bit to configure the Clock Polarity */
      scml2::bitfield< unsigned int > CPOL;
      /* Bit to configure the Clock Phase */
      scml2::bitfield< unsigned int > CPHA;
      /* Bit to configure the MSB or LSB transmit first option */
      scml2::bitfield< unsigned int > LSBFE;
      /* Clock Prescaler */
      scml2::bitfield< unsigned int > PCSSCK;
    };
    struct SR_type : public scml2::reg< unsigned int > {
      ~SR_type();
      SR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset, ModelBaseType& model_);
      using scml2::reg< unsigned int >::operator=;
      using scml2::reg< unsigned int >::operator+=;
      using scml2::reg< unsigned int >::operator-=;
      using scml2::reg< unsigned int >::operator/=;
      using scml2::reg< unsigned int >::operator*=;
      using scml2::reg< unsigned int >::operator%=;
      using scml2::reg< unsigned int >::operator^=;
      using scml2::reg< unsigned int >::operator&=;
      using scml2::reg< unsigned int >::operator|=;
      using scml2::reg< unsigned int >::operator>>=;
      using scml2::reg< unsigned int >::operator<<=;
      using scml2::reg< unsigned int >::operator--;
      using scml2::reg< unsigned int >::operator++;
      using scml2::reg< unsigned int >::operator unsigned int;
      /* Transfer Complete Flag */
      scml2::bitfield< unsigned int > TCF;
      /* Transmit and Receive Status Flag */
      scml2::bitfield< unsigned int > TXRXS;
      /* End of Queue Flag */
      scml2::bitfield< unsigned int > EOQF;
      /* Transmit FIFO Underflow Flag */
      scml2::bitfield< unsigned int > TFUF;
      /* Transmit FIFO Fill Flag */
      scml2::bitfield< unsigned int > TFFF;
      /* Receive FIFO Overflow Flag */
      scml2::bitfield< unsigned int > RFOF;
      /* Receive FIFO Drain Flag */
      scml2::bitfield< unsigned int > RFDF;
      scml2::bitfield_proxy< unsigned int > reserved4;
      /* CRC Error bit added */
      scml2::bitfield_proxy< unsigned int > CRC_ERROR;
      scml2::bitfield_proxy< unsigned int > reserved5;
    };
    struct PUSHR_type : public scml2::reg< unsigned int > {
      ~PUSHR_type();
      PUSHR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset);
      using scml2::reg< unsigned int >::operator=;
      using scml2::reg< unsigned int >::operator+=;
      using scml2::reg< unsigned int >::operator-=;
      using scml2::reg< unsigned int >::operator/=;
      using scml2::reg< unsigned int >::operator*=;
      using scml2::reg< unsigned int >::operator%=;
      using scml2::reg< unsigned int >::operator^=;
      using scml2::reg< unsigned int >::operator&=;
      using scml2::reg< unsigned int >::operator|=;
      using scml2::reg< unsigned int >::operator>>=;
      using scml2::reg< unsigned int >::operator<<=;
      using scml2::reg< unsigned int >::operator--;
      using scml2::reg< unsigned int >::operator++;
      using scml2::reg< unsigned int >::operator unsigned int;
      /* Continuous Selection Format */
      scml2::bitfield< unsigned int > CONT;
      /* CTAS register selection */
      scml2::bitfield< unsigned int > CTAS;
      /* End Of Queue */
      scml2::bitfield< unsigned int > EOQ;
      /* Clear Transfer Counter */
      scml2::bitfield< unsigned int > CTCNT;
      /* Peripheral Chip Select */
      scml2::bitfield< unsigned int > PCS;
      /* Data to transmit */
      scml2::bitfield< unsigned int > TXDATA;
    };
    scml2::objects::router<unsigned int> bus_reg_in_router;
    TX_PATHType TX_PATH;
    RX_PATHType RX_PATH;
    scml2::objects::variable<unsigned int> SHIFT_REGISTER;
    scml2::objects::action CRC_MOD;
    scml2::base::actions m_actions;
    scml2::tlm2_ft_target_port_pe<32> bus_reg_in_protocol_engine;
    tlm_ft_spi_protocol_engine Serial_IO_protocol_engine;
    scml2::reset_slave_engine rst_in_protocol_engine;
    scml2::clock_slave_engine spi_clk_protocol_engine;
    scml2::clock_slave_engine clk_in_protocol_engine;
    scml2::interrupt_master_engine tfuf_irq_protocol_engine;
    scml2::interrupt_master_engine tfff_irq_protocol_engine;
    scml2::interrupt_master_engine rfof_irq_protocol_engine;
    scml2::interrupt_master_engine rfdf_irq_protocol_engine;
    scml2::memory< unsigned int > mRegs;
    /* Module Configuration Register */
    MCR_type MCR;
    unsigned int MCR_reset_value;
    unsigned int MCR_reset_mask;
    /* Clock and Transfer Attributes Register */
    scml2::vector< CTAR_type > CTAR;
    unsigned int CTAR_reset_value;
    unsigned int CTAR_reset_mask;
    /* Status Register */
    SR_type SR;
    unsigned int SR_reset_value;
    unsigned int SR_reset_mask;
    /* Request Select and Enable Register */
    scml2::reg< unsigned int > RSER;
    unsigned int RSER_reset_value;
    /* Push Transmit FIFO Register */
    PUSHR_type PUSHR;
    unsigned int PUSHR_reset_value;
    /* Pop Recieve FIFO Register */
    scml2::reg< unsigned int > POPR;
    unsigned int POPR_reset_value;
private:
};
#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif


