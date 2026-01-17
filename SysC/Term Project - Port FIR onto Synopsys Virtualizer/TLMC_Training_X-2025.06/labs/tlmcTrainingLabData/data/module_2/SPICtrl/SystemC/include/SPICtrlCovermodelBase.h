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
 * CHECKSUM:b0771e75942610d96be811231b2c965d6072c9d2
 ***************************************************************************/
 
#pragma once

#include "scml2_coverage.h"
#include "SPICtrl.h"

#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif


class SPICtrlCovermodelBase
#ifdef SNPS_SLS_VP_COVERAGE
  : public scml2::cov::covergroup
#endif
{
public:
 SPICtrlCovermodelBase(const std::string& test_name, SPICtrl& t)
 #ifdef SNPS_SLS_VP_COVERAGE
  : scml2::cov::covergroup("SPICtrl", test_name, &t)
  , enable_check_clocks(t.enable_check_clocks, "enable_check_clocks")
  , target_id(t.target_id, "target_id")
  , fifo_size(t.fifo_size, "fifo_size")
  , version(t.version, "version")
  , spi_clk(t.spi_clk, "spi_clk")
  , clk_in(t.clk_in, "clk_in")
  , tfuf_irq(t.tfuf_irq, "tfuf_irq")
  , tfff_irq(t.tfff_irq, "tfff_irq")
  , rfof_irq(t.rfof_irq, "rfof_irq")
  , rfdf_irq(t.rfdf_irq, "rfdf_irq")
  , rst_in(t.rst_in, "rst_in")
  , bus_reg_in(t.bus_reg_in, "bus_reg_in")
  , mRegs(t.mRegs, "mRegs")
  , MCR(t.MCR, "mRegs.MCR", this)
  , CTAR(t.CTAR, "mRegs.CTAR", this)
  , SR(t.SR, "mRegs.SR", this)
  , RSER(t.RSER, "mRegs.RSER")
  , PUSHR(t.PUSHR, "mRegs.PUSHR", this)
  , POPR(t.POPR, "mRegs.POPR")
 #endif
 {
 #ifdef SNPS_SLS_VP_COVERAGE
  mRegs.disable();
  MCR.configure_default_bins(0);
  CTAR.configure_default_bins(0);
  SR.configure_default_bins(0);
  RSER.configure_default_bins(0);
  PUSHR.configure_default_bins(0);
  POPR.configure_default_bins(0);

  this->enable_check_clocks.bins("allowed_values").values({false, true}).array(2);
  this->target_id.disable();
  this->fifo_size.disable();
  this->version.bins("allowed_values").values({10003,10200}).array(2);
  this->version.default_bin().illegal();
 #endif
 }
 #ifdef SNPS_SLS_VP_COVERAGE
protected:
 scml2::cov::scml_property<bool> enable_check_clocks;
 scml2::cov::scml_property<unsigned int> target_id;
 scml2::cov::scml_property<unsigned int> fifo_size;
 scml2::cov::scml_property<int> version;
 scml2::cov::scml_clock spi_clk;
 scml2::cov::scml_clock clk_in;
 scml2::cov::sc_out<bool> tfuf_irq;
 scml2::cov::sc_out<bool> tfff_irq;
 scml2::cov::sc_out<bool> rfof_irq;
 scml2::cov::sc_out<bool> rfdf_irq;
 scml2::cov::sc_in<bool> rst_in;
 scml2::cov::socket<scml2::ft_target_socket<32> > bus_reg_in;
 scml2::cov::memory<unsigned int> mRegs;
 struct MCR_type : public scml2::cov::reg<unsigned int> 
 {
   MCR_type(SPICtrl::MCR_type& _reg, const std::string& name, SPICtrlCovermodelBase * model = 0)
    : scml2::cov::reg<unsigned int>(_reg, name)
   , MSTR(_reg.MSTR, name + ".MSTR")
   , PCSSE(_reg.PCSSE, name + ".PCSSE")
   , UFL_TXF(_reg.UFL_TXF, name + ".UFL_TXF")
   , OFL_RXF(_reg.OFL_RXF, name + ".OFL_RXF")
   , MDIS(_reg.MDIS, name + ".MDIS")
   , CLR_TXF(_reg.CLR_TXF, name + ".CLR_TXF")
   , CLR_RXF(_reg.CLR_RXF, name + ".CLR_RXF")
  {
   disable();
   {
     MSTR.bins("input_mode","").value(SPICtrl::MCR_type::MCR_MSTR_type::input_mode);
     MSTR.bins("driver_mode","").value(SPICtrl::MCR_type::MCR_MSTR_type::driver_mode);
     {
       const unsigned int width =  0 - 0 + 1;
       const unsigned int enum_count = 2;
       if ( enum_count !=  (1ull << width) ) {
         // coverity[dead_error_line]
         MSTR.default_bin("undefined");
       }
     }
   }
   {
     PCSSE.bins("chip_select_mode","").value(SPICtrl::MCR_type::MCR_PCSSE_type::chip_select_mode);
     PCSSE.bins("strobe_mode","").value(SPICtrl::MCR_type::MCR_PCSSE_type::strobe_mode);
     {
       const unsigned int width =  6 - 6 + 1;
       const unsigned int enum_count = 2;
       if ( enum_count !=  (1ull << width) ) {
         // coverity[dead_error_line]
         PCSSE.default_bin("undefined");
       }
     }
   }
   UFL_TXF.configure_default_bins(0);
   OFL_RXF.configure_default_bins(0);
   MDIS.configure_default_bins(0);
   CLR_TXF.configure_default_bins(0);
   CLR_RXF.configure_default_bins(0);
  }
  virtual void disable_all()
  {
   scml2::cov::reg<unsigned int>::disable_all();
   this->MSTR.disable();
   this->PCSSE.disable();
   this->UFL_TXF.disable();
   this->OFL_RXF.disable();
   this->MDIS.disable();
   this->CLR_TXF.disable();
   this->CLR_RXF.disable();
  }
  virtual void access_all(scml2::cov::access_type at)
  {
   scml2::cov::reg<unsigned int>::access_all(at);
   this->MSTR.access(at);
   this->PCSSE.access(at);
   this->UFL_TXF.access(at);
   this->OFL_RXF.access(at);
   this->MDIS.access(at);
   this->CLR_TXF.access(at);
   this->CLR_RXF.access(at);
  }
  scml2::cov::bitfield<unsigned int> MSTR;
  scml2::cov::bitfield<unsigned int> PCSSE;
  scml2::cov::bitfield<unsigned int> UFL_TXF;
  scml2::cov::bitfield<unsigned int> OFL_RXF;
  scml2::cov::bitfield<unsigned int> MDIS;
  scml2::cov::bitfield<unsigned int> CLR_TXF;
  scml2::cov::bitfield<unsigned int> CLR_RXF;
 };
  MCR_type MCR;
 struct CTAR_type : public scml2::cov::reg<unsigned int> 
 {
   CTAR_type(scml2::vector<SPICtrl::CTAR_type >& _reg, const std::string& name, SPICtrlCovermodelBase * model = 0)
    : scml2::cov::reg<unsigned int>(_reg, name)
   , FMSZ(_reg, name + ".FMSZ", &SPICtrl::CTAR_type::FMSZ)
   , CPOL(_reg, name + ".CPOL", &SPICtrl::CTAR_type::CPOL)
   , bf(_reg, name + ".bf", &SPICtrl::CTAR_type::bf)
   , LSBFE(_reg, name + ".LSBFE", &SPICtrl::CTAR_type::LSBFE)
   , PCSSCK(_reg, name + ".PCSSCK", &SPICtrl::CTAR_type::PCSSCK)
  {
   disable();
   FMSZ.configure_default_bins(0);
   CPOL.configure_default_bins(0);
   bf.configure_default_bins(0);
   LSBFE.configure_default_bins(0);
   PCSSCK.configure_default_bins(0);
  }
  virtual void disable_all()
  {
   scml2::cov::reg<unsigned int>::disable_all();
   this->FMSZ.disable();
   this->CPOL.disable();
   this->bf.disable();
   this->LSBFE.disable();
   this->PCSSCK.disable();
  }
  virtual void access_all(scml2::cov::access_type at)
  {
   scml2::cov::reg<unsigned int>::access_all(at);
   this->FMSZ.access(at);
   this->CPOL.access(at);
   this->bf.access(at);
   this->LSBFE.access(at);
   this->PCSSCK.access(at);
  }
  scml2::cov::bitfield<unsigned int> FMSZ;
  scml2::cov::bitfield<unsigned int> CPOL;
  scml2::cov::bitfield<unsigned int> bf;
  scml2::cov::bitfield<unsigned int> LSBFE;
  scml2::cov::bitfield<unsigned int> PCSSCK;
 };
  CTAR_type CTAR;
 struct SR_type : public scml2::cov::reg<unsigned int> 
 {
   SR_type(SPICtrl::SR_type& _reg, const std::string& name, SPICtrlCovermodelBase * model = 0)
    : scml2::cov::reg<unsigned int>(_reg, name)
   , TCF(_reg.TCF, name + ".TCF")
   , TXRXS(_reg.TXRXS, name + ".TXRXS")
   , EOQF(_reg.EOQF, name + ".EOQF")
   , TFUF(_reg.TFUF, name + ".TFUF")
   , TFFF(_reg.TFFF, name + ".TFFF")
   , RFOF(_reg.RFOF, name + ".RFOF")
   , RFDF(_reg.RFDF, name + ".RFDF")
   , reserved4(_reg.reserved4, name + ".reserved4")
   , CRC_ERROR(_reg.CRC_ERROR, name + ".CRC_ERROR")
   , reserved5(_reg.reserved5, name + ".reserved5")
  {
   disable();
   TCF.configure_default_bins(0);
   TXRXS.configure_default_bins(0);
   EOQF.configure_default_bins(0);
   TFUF.configure_default_bins(0);
   TFFF.configure_default_bins(0);
   RFOF.configure_default_bins(0);
   RFDF.configure_default_bins(0);
   reserved4.disable();
   CRC_ERROR.configure_default_bins(0);
   reserved5.configure_default_bins(0);
  }
  virtual void disable_all()
  {
   scml2::cov::reg<unsigned int>::disable_all();
   this->TCF.disable();
   this->TXRXS.disable();
   this->EOQF.disable();
   this->TFUF.disable();
   this->TFFF.disable();
   this->RFOF.disable();
   this->RFDF.disable();
   this->reserved4.disable();
   this->CRC_ERROR.disable();
   this->reserved5.disable();
  }
  virtual void access_all(scml2::cov::access_type at)
  {
   scml2::cov::reg<unsigned int>::access_all(at);
   this->TCF.access(at);
   this->TXRXS.access(at);
   this->EOQF.access(at);
   this->TFUF.access(at);
   this->TFFF.access(at);
   this->RFOF.access(at);
   this->RFDF.access(at);
   this->reserved4.access(at);
   this->CRC_ERROR.access(at);
   this->reserved5.access(at);
  }
  scml2::cov::bitfield<unsigned int> TCF;
  scml2::cov::bitfield<unsigned int> TXRXS;
  scml2::cov::bitfield<unsigned int> EOQF;
  scml2::cov::bitfield<unsigned int> TFUF;
  scml2::cov::bitfield<unsigned int> TFFF;
  scml2::cov::bitfield<unsigned int> RFOF;
  scml2::cov::bitfield<unsigned int> RFDF;
  scml2::cov::bitfield<unsigned int> reserved4;
  scml2::cov::bitfield<unsigned int> CRC_ERROR;
  scml2::cov::bitfield<unsigned int> reserved5;
 };
  SR_type SR;
  scml2::cov::reg<unsigned int> RSER;
 struct PUSHR_type : public scml2::cov::reg<unsigned int> 
 {
   PUSHR_type(SPICtrl::PUSHR_type& _reg, const std::string& name, SPICtrlCovermodelBase * model = 0)
    : scml2::cov::reg<unsigned int>(_reg, name)
   , CONT(_reg.CONT, name + ".CONT")
   , CTAS(_reg.CTAS, name + ".CTAS")
   , EOQ(_reg.EOQ, name + ".EOQ")
   , CTCNT(_reg.CTCNT, name + ".CTCNT")
   , PCS(_reg.PCS, name + ".PCS")
   , TXDATA(_reg.TXDATA, name + ".TXDATA")
  {
   disable();
   CONT.configure_default_bins(0);
   CTAS.configure_default_bins(0);
   EOQ.configure_default_bins(0);
   CTCNT.configure_default_bins(0);
   PCS.configure_default_bins(0);
   TXDATA.configure_default_bins(0);
  }
  virtual void disable_all()
  {
   scml2::cov::reg<unsigned int>::disable_all();
   this->CONT.disable();
   this->CTAS.disable();
   this->EOQ.disable();
   this->CTCNT.disable();
   this->PCS.disable();
   this->TXDATA.disable();
  }
  virtual void access_all(scml2::cov::access_type at)
  {
   scml2::cov::reg<unsigned int>::access_all(at);
   this->CONT.access(at);
   this->CTAS.access(at);
   this->EOQ.access(at);
   this->CTCNT.access(at);
   this->PCS.access(at);
   this->TXDATA.access(at);
  }
  scml2::cov::bitfield<unsigned int> CONT;
  scml2::cov::bitfield<unsigned int> CTAS;
  scml2::cov::bitfield<unsigned int> EOQ;
  scml2::cov::bitfield<unsigned int> CTCNT;
  scml2::cov::bitfield<unsigned int> PCS;
  scml2::cov::bitfield<unsigned int> TXDATA;
 };
  PUSHR_type PUSHR;
  scml2::cov::reg<unsigned int> POPR;
 #endif
};
#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif



