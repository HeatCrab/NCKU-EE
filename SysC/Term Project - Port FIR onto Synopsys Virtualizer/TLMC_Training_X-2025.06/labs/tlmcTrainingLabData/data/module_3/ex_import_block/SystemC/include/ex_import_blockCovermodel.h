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
 * CHECKSUM:8f92beebaae3d7980c34b0dfb92cd40077c744c8
 ***************************************************************************/
 
#pragma once

#include "scml2_coverage.h"

#include "ex_import_blockCovermodelBase.h"


template<typename Ttn = int, bool Tb = false, int Tint = 1>
class ex_import_blockCovermodel
  : public ex_import_blockCovermodelBase<Ttn, Tb, Tint>
{
public:
 ex_import_blockCovermodel(const std::string& test_name, ex_import_block<Ttn, Tb, Tint>& t)
  : ex_import_blockCovermodelBase<Ttn, Tb, Tint>(test_name, t)
 {
#ifdef SNPS_SLS_VP_COVERAGE
#endif
 }

 virtual ~ex_import_blockCovermodel() {
  this->write_log();
 }
};

