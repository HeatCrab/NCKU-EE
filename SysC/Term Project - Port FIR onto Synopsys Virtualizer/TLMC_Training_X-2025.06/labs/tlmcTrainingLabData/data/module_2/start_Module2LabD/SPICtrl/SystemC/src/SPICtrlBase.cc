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
 * CHECKSUM:806e122bf7265cda0e1a5640d4b5d9e0b455cab3
 ***************************************************************************/
 

 
 // Warning: This is an auto-generated file. All changes to this file will be overwritten.


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


#include "SPICtrlBase.h"


#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif

SPICtrlBase::MCR_type::~MCR_type() {};

SPICtrlBase::MCR_type::MCR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset) :
    scml2::reg< unsigned int >(name, memory, offset),
    MSTR(sc_core::sc_gen_unique_name("MSTR", true), *this, 0, 1),
    PCSSE(sc_core::sc_gen_unique_name("PCSSE", true), *this, 6, 1),
    UFL_TXF(sc_core::sc_gen_unique_name("UFL_TXF", true), *this, 8, 4),
    OFL_RXF(sc_core::sc_gen_unique_name("OFL_RXF", true), *this, 12, 4),
    MDIS(sc_core::sc_gen_unique_name("MDIS", true), *this, 17, 1),
    CLR_TXF(sc_core::sc_gen_unique_name("CLR_TXF", true), *this, 20, 1),
    CLR_RXF(sc_core::sc_gen_unique_name("CLR_RXF", true), *this, 21, 1) {}

SPICtrlBase::MCR_type::MCR_MSTR_type::~MCR_MSTR_type() {};

SPICtrlBase::MCR_type::MCR_MSTR_type::MCR_MSTR_type(const std::string& name, scml2::reg< unsigned int >& parent, unsigned int offset, unsigned int size) :
    scml2::bitfield< unsigned int >(name, parent, offset, size) {}

SPICtrlBase::MCR_type::MCR_PCSSE_type::~MCR_PCSSE_type() {};

SPICtrlBase::MCR_type::MCR_PCSSE_type::MCR_PCSSE_type(const std::string& name, scml2::reg< unsigned int >& parent, unsigned int offset, unsigned int size) :
    scml2::bitfield< unsigned int >(name, parent, offset, size) {}

SPICtrlBase::CTAR_type::~CTAR_type() {};

SPICtrlBase::CTAR_type::CTAR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset) :
    scml2::reg< unsigned int >(name, memory, offset),
    FMSZ(sc_core::sc_gen_unique_name("FMSZ", true), *this, 0, 5),
    CPOL(sc_core::sc_gen_unique_name("CPOL", true), *this, 5, 1),
    CPHA(sc_core::sc_gen_unique_name("CPHA", true), *this, 6, 1),
    LSBFE(sc_core::sc_gen_unique_name("LSBFE", true), *this, 7, 1),
    PCSSCK(sc_core::sc_gen_unique_name("PCSSCK", true), *this, 8, 2) {}

SPICtrlBase::SR_type::~SR_type() {};

SPICtrlBase::SR_type::SR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset, ModelBaseType& model_) :
    scml2::reg< unsigned int >(name, memory, offset),
    TCF(sc_core::sc_gen_unique_name("TCF", true), *this, 0, 1),
    TXRXS(sc_core::sc_gen_unique_name("TXRXS", true), *this, 1, 1),
    EOQF(sc_core::sc_gen_unique_name("EOQF", true), *this, 3, 1),
    TFUF(sc_core::sc_gen_unique_name("TFUF", true), *this, 4, 1),
    TFFF(sc_core::sc_gen_unique_name("TFFF", true), *this, 6, 1),
    RFOF(sc_core::sc_gen_unique_name("RFOF", true), *this, 12, 1),
    RFDF(sc_core::sc_gen_unique_name("RFDF", true), *this, 14, 1),
    reserved4(sc_core::sc_gen_unique_name("reserved4", true), *this, 15, 17, (bool)(model_.version < 10200)),
    CRC_ERROR(sc_core::sc_gen_unique_name("CRC_ERROR", true), *this, 31, 1, (bool)(model_.version >= 10200)),
    reserved5(sc_core::sc_gen_unique_name("reserved5", true), *this, 15, 16, (bool)(model_.version >= 10200)) {}

SPICtrlBase::PUSHR_type::~PUSHR_type() {};

SPICtrlBase::PUSHR_type::PUSHR_type(const std::string& name, scml2::toplevel_memory_base& memory, unsigned long long offset) :
    scml2::reg< unsigned int >(name, memory, offset),
    CONT(sc_core::sc_gen_unique_name("CONT", true), *this, 0, 1),
    CTAS(sc_core::sc_gen_unique_name("CTAS", true), *this, 1, 3),
    EOQ(sc_core::sc_gen_unique_name("EOQ", true), *this, 4, 1),
    CTCNT(sc_core::sc_gen_unique_name("CTCNT", true), *this, 5, 1),
    PCS(sc_core::sc_gen_unique_name("PCS", true), *this, 8, 8),
    TXDATA(sc_core::sc_gen_unique_name("TXDATA", true), *this, 16, 16) {}


#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif


