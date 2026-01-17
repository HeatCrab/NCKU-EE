#############################################################################
# Copyright 1996-2024 Synopsys, Inc.                                        #
#                                                                           #
# This Synopsys software and all associated documentation are proprietary   #
# to Synopsys, Inc. and may only be used pursuant to the terms and          #
# conditions of a written license agreement with Synopsys, Inc.             #
# All other use, reproduction, modification, or distribution of the         #
# Synopsys software or the associated documentation is strictly prohibited. #
#############################################################################

namespace eval ::SPICtrl {
proc handle_block_instantiated {instance} {
  if {[info exists ::env(SNPS_VS_PCSH_IN_VDKC_BACKEND_MODE)]} { return }
  ::pct::update_port_array $instance
}
proc handle_parameter_changed {instance parameter_set parameter_name {old_value 0}} {
  if {[info exists ::env(SNPS_VS_PCSH_IN_VDKC_BACKEND_MODE)]} { return }
  if {$parameter_set != "Template Arguments" && $parameter_set != "Scml Properties"} { return }
  ::pct::update_port_array $instance
}
}
