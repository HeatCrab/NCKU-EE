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
 * CHECKSUM:d11f3437e14ba20008d589491a40fdfa01baf62a
 ***************************************************************************/
 
#pragma once

#include "scml2_coverage.h"
#include "/home/user1/sc25/sc2568/TLMCreation_Quickstart_Training_X-2025.06/TLMC_Training_X-2025.06/labs/tlmcTrainingLabData/tlmcTrainingLabData/data/module_3/ImportSystemC/include/block.h"

#ifdef _WIN32
#pragma optimize("g",off)
#else
#pragma GCC push_options
#pragma GCC optimize("O0")
#endif

template<typename Ttn = int, bool Tb = false, int Tint = 1>
class ex_import_blockCovermodelBase
#ifdef SNPS_SLS_VP_COVERAGE
  : public scml2::cov::covergroup
#endif
{
public:
 ex_import_blockCovermodelBase(const std::string& test_name, ex_import_block<Ttn, Tb, Tint>& t)
 #ifdef SNPS_SLS_VP_COVERAGE
  : scml2::cov::covergroup("ex_import_block<Ttn, Tb, Tint>", test_name, &t)
  , p_clk(t.p_clk, "p_clk")
  , in(t.in, "in")
  , p_reset(t.p_reset, "p_reset")
  , socket(t.socket, "socket")
 #endif
 {
 #ifdef SNPS_SLS_VP_COVERAGE
 #endif
 }
 #ifdef SNPS_SLS_VP_COVERAGE
protected:
 scml2::cov::scml_clock p_clk;
 scml2::cov::sc_in<bool> in;
 scml2::cov::sc_in<bool> p_reset;
 scml2::cov::socket<tlm::tlm_target_socket<32 > > socket;
 #endif
};
#ifdef _WIN32
#pragma optimize("",on)
#else
#pragma GCC pop_options
#endif



