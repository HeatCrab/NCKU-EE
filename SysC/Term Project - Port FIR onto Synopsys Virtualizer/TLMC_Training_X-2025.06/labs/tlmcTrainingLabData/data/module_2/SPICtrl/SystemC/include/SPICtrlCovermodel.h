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
 * CHECKSUM:79fbd38808c90e55f6e04e6595ad7bad01def312
 ***************************************************************************/
 
#pragma once

#include "scml2_coverage.h"

#include "SPICtrlCovermodelBase.h"



class SPICtrlCovermodel
  : public SPICtrlCovermodelBase
{
public:
 SPICtrlCovermodel(const std::string& test_name, SPICtrl& t)
  : SPICtrlCovermodelBase(test_name, t)
 {
#ifdef SNPS_SLS_VP_COVERAGE
#endif
 }

 virtual ~SPICtrlCovermodel() {
  this->write_log();
 }
};

