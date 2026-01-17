#############################################################################
# Copyright 1996-2024 Synopsys, Inc.                                        #
#                                                                           #
# This Synopsys software and all associated documentation are proprietary   #
# to Synopsys, Inc. and may only be used pursuant to the terms and          #
# conditions of a written license agreement with Synopsys, Inc.             #
# All other use, reproduction, modification, or distribution of the         #
# Synopsys software or the associated documentation is strictly prohibited. #
#############################################################################

if {[file exists [file normalize [file dirname [info script]]]/ex_import_block_import_user_pre.tcl]} { source [file normalize [file dirname [info script]]]/ex_import_block_import_user_pre.tcl }
::pct::create_block ex_import_block
::pct::add_generator ex_import_block parameter_change_cb ::ex_import_block::handle_parameter_changed "[file normalize [file dirname [info script]]]/ex_import_block_callback.tcl" 100 parameter_change false false
::pct::add_generator ex_import_block instantiate_cb ::ex_import_block::handle_block_instantiated "[file normalize [file dirname [info script]]]/ex_import_block_callback.tcl" 100 instantiate
::pct::create_encap ex_import_block ex_import_block
::pct::create_encap_constructor ex_import_block/ex_import_block
::pct::set_default_constructor ex_import_block/ex_import_block ex_import_block()
::pct::create_template_parameter ex_import_block/ex_import_block Ttn type
::pct::set_template_parameter_property ex_import_block/ex_import_block Ttn default_value int
::pct::set_param_visibility ex_import_block/ex_import_block "Template Arguments" Ttn visible
::pct::set_param_editability ex_import_block/ex_import_block "Template Arguments" Ttn until_simulation_build
::pct::set_param_sweepable ex_import_block/ex_import_block "Template Arguments" Ttn false
::pct::create_template_parameter ex_import_block/ex_import_block Tb boolean
::pct::set_template_parameter_property ex_import_block/ex_import_block Tb default_value false
::pct::set_param_visibility ex_import_block/ex_import_block "Template Arguments" Tb visible
::pct::set_param_editability ex_import_block/ex_import_block "Template Arguments" Tb until_simulation_build
::pct::set_param_sweepable ex_import_block/ex_import_block "Template Arguments" Tb false
::pct::create_template_parameter ex_import_block/ex_import_block Tint integer
::pct::set_template_parameter_property ex_import_block/ex_import_block Tint default_value 1
::pct::set_param_visibility ex_import_block/ex_import_block "Template Arguments" Tint visible
::pct::set_param_editability ex_import_block/ex_import_block "Template Arguments" Tint until_simulation_build
::pct::set_param_sweepable ex_import_block/ex_import_block "Template Arguments" Tint false
::pct::create_scml_property ex_import_block/ex_import_block p_uint integer
::pct::set_scml_property_property ex_import_block/ex_import_block p_uint allowed_range_min 0
::pct::set_scml_property_property ex_import_block/ex_import_block p_uint allowed_range_max 4294967295
::pct::set_scml_property_property ex_import_block/ex_import_block p_uint default_value 2
::pct::set_param_visibility ex_import_block/ex_import_block "Scml Properties" p_uint visible
::pct::set_param_editability ex_import_block/ex_import_block "Scml Properties" p_uint until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "Scml Properties" p_uint true
::pct::create_scml_property ex_import_block/ex_import_block p_bool boolean
::pct::set_scml_property_property ex_import_block/ex_import_block p_bool default_value true
::pct::set_param_visibility ex_import_block/ex_import_block "Scml Properties" p_bool visible
::pct::set_param_editability ex_import_block/ex_import_block "Scml Properties" p_bool until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "Scml Properties" p_bool true
::pct::create_scml_property ex_import_block/ex_import_block p_double double
::pct::set_scml_property_property ex_import_block/ex_import_block p_double default_value 3.14
::pct::set_param_visibility ex_import_block/ex_import_block "Scml Properties" p_double visible
::pct::set_param_editability ex_import_block/ex_import_block "Scml Properties" p_double until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "Scml Properties" p_double true
::pct::create_scml_property ex_import_block/ex_import_block p_string string
::pct::set_scml_property_property ex_import_block/ex_import_block p_string default_value {one}
::pct::set_param_visibility ex_import_block/ex_import_block "Scml Properties" p_string visible
::pct::set_param_editability ex_import_block/ex_import_block "Scml Properties" p_string until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "Scml Properties" p_string true
::pct::add_constructor_parameter ex_import_block/ex_import_block ex_import_block() ca_int integer
::pct::set_constructor_parameter_property ex_import_block/ex_import_block ex_import_block(ca_int) ca_int allowed_range_min -2147483648
::pct::set_constructor_parameter_property ex_import_block/ex_import_block ex_import_block(ca_int) ca_int allowed_range_max 2147483647
::pct::set_constructor_parameter_property ex_import_block/ex_import_block ex_import_block(ca_int) ca_int default_value 0
::pct::set_param_visibility ex_import_block/ex_import_block ex_import_block(ca_int) "Constructor Arguments" ca_int visible
::pct::set_param_editability ex_import_block/ex_import_block ex_import_block(ca_int) "Constructor Arguments" ca_int until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block ex_import_block(ca_int) "Constructor Arguments" ca_int false
::pct::add_constructor_parameter ex_import_block/ex_import_block ex_import_block(ca_int) ca_bool boolean
::pct::set_constructor_parameter_property ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool)" ca_bool default_value true
::pct::set_param_visibility ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool)" "Constructor Arguments" ca_bool visible
::pct::set_param_editability ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool)" "Constructor Arguments" ca_bool until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool)" "Constructor Arguments" ca_bool false
::pct::add_constructor_parameter ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool)" ca_double double
::pct::set_constructor_parameter_property ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double)" ca_double default_value 0.0
::pct::set_param_visibility ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double)" "Constructor Arguments" ca_double visible
::pct::set_param_editability ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double)" "Constructor Arguments" ca_double until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double)" "Constructor Arguments" ca_double false
::pct::add_constructor_parameter ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double)" ca_string string
::pct::set_constructor_parameter_property ex_import_block/ex_import_block {ex_import_block(ca_int, ca_bool, ca_double, ca_string)} ca_string default_value {any}
::pct::set_param_visibility ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double, ca_string)" "Constructor Arguments" ca_string visible
::pct::set_param_editability ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double, ca_string)" "Constructor Arguments" ca_string until_simulation_start
::pct::set_param_sweepable ex_import_block/ex_import_block "ex_import_block(ca_int, ca_bool, ca_double, ca_string)" "Constructor Arguments" ca_string false
::pct::create_bca_encap_port ex_import_block/ex_import_block in bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:ex_import_block in in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:ex_import_block/in SYSTEM_LIBRARY:Default
::pct::map_encap_port SYSTEM_LIBRARY:ex_import_block/ex_import_block/in in pin
::pct::set_param_value SYSTEM_LIBRARY:ex_import_block/in "Port Properties" MasterSlaveness Slave
::pct::set_param_value SYSTEM_LIBRARY:ex_import_block/in:ex_import_block "Protocol Common Parameters" data_width bitwidth(bool)
if {![::pct::is_library_open TLM2_PROTOCOLS]} {
    ::pct::open_library TLM2_PROTOCOLS
}
::pct::create_tlm_encap_port ex_import_block/ex_import_block socket "tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types >, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types >, 1, sc_core::SC_ONE_OR_MORE_BOUND>" TARGET_SOCKET REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:ex_import_block socket None
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:ex_import_block/socket TLM2_PROTOCOLS:tlm2_gp
::pct::set_param_value SYSTEM_LIBRARY:ex_import_block/socket "Port Properties" MasterSlaveness Slave
::pct::map_encap_port SYSTEM_LIBRARY:ex_import_block/ex_import_block/socket socket
::pct::add_target_location SYSTEM_LIBRARY:ex_import_block/socket MemoryMap
::pct::set_target_location_type SYSTEM_LIBRARY:ex_import_block/socket:MemoryMap block
::pct::set_target_location_size SYSTEM_LIBRARY:ex_import_block/socket:MemoryMap 12
::pct::set_target_location_address SYSTEM_LIBRARY:ex_import_block/socket:MemoryMap 0 0x0
::pct::create_bca_encap_port ex_import_block/ex_import_block p_reset bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:ex_import_block p_reset in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:ex_import_block/p_reset SYSTEM_LIBRARY:RESET
::pct::map_encap_port SYSTEM_LIBRARY:ex_import_block/ex_import_block/p_reset p_reset pin
::pct::set_param_value SYSTEM_LIBRARY:ex_import_block/p_reset "Port Properties" MasterSlaveness Slave
::pct::RESET::upgrade_port ex_import_block/ex_import_block p_reset false
::pct::create_bca_encap_port ex_import_block/ex_import_block p_clk bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:ex_import_block p_clk in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:ex_import_block/p_clk SYSTEM_LIBRARY:CLOCK
::pct::map_encap_port SYSTEM_LIBRARY:ex_import_block/ex_import_block/p_clk p_clk pin
::pct::set_param_value SYSTEM_LIBRARY:ex_import_block/p_clk "Port Properties" MasterSlaveness Slave
::pct::CLOCK::upgrade_port ex_import_block/ex_import_block p_clk
::pct::create_encap_config SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild
::pct::set_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build enabled true
::pct::set_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build debug false
::pct::set_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build optimized true
::pct::set_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build assertions false
::pct::set_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build dynamic_library true
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build target ex_import_block *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build target_directory "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/ex_import_block.dladapter.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build header_file /home/user1/sc25/sc2568/TLMCreation_Quickstart_Training_X-2025.06/TLMC_Training_X-2025.06/labs/tlmcTrainingLabData/tlmcTrainingLabData/data/module_3/ImportSystemC/include/block.h *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path "[file normalize [file dirname [info script]]]/../.." *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path "[file normalize [file dirname [info script]]]/../../SystemC/include" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/tlmcreator/templates/models/common/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/IP_common/AMBA_TLM2_BL/AMBA-PV/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/IP_common/AMBA_TLM2_BL/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/common/include/tlm_serial *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_can_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_spi_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_lin_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build template_instance "<int, true, 0>" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build template_instance "<int, false, 0>" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build template_instance "<int, true, 1>" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build compile_flag "-fvisibility=hidden" gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build link_flag -fPIC gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build link_flag -Wl,--no-undefined gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild build define SC_INCLUDE_DYNAMIC_PROCESSES "" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package header_file /home/user1/sc25/sc2568/TLMCreation_Quickstart_Training_X-2025.06/TLMC_Training_X-2025.06/labs/tlmcTrainingLabData/tlmcTrainingLabData/data/module_3/ImportSystemC/include/block.h *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/ex_import_blockCovermodel.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package dynamic_load ex_import_block %(EXPORTHOME)%/simulation/FastBuild/ *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package dynamic_load ex_import_block "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package define SC_INCLUDE_DYNAMIC_PROCESSES "" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package include_path "[file normalize [file dirname [info script]]]/../.." *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package include_path "[file normalize [file dirname [info script]]]/../../SystemC/include" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package include_path #(SNPS_VP_HOME)#/tlmcreator/templates/models/common/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/ex_import_block.dll" simulation/FastBuild/ msvc-14.34-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/ex_import_block.dll" simulation/FastBuild/ msvc-14.38-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/libex_import_block.so" simulation/FastBuild/ gcc-9.5-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/libex_import_block.so" simulation/FastBuild/ gcc-12.3-64
if {[file exists [file normalize [file dirname [info script]]]/../../SystemC/src/ex_import_block.rc]} {
::pct::add_encap_config_setting ex_import_block/ex_import_block FastBuild build resource_file "[file normalize [file dirname [info script]]]/../../SystemC/src/ex_import_block.rc"
}
::pct::add_encap_config_setting ex_import_block/ex_import_block FastBuild build component_helper coverage "::ex_import_blockCovermodel<Ttn, Tb, Tint>"
::pct::add_encap_config_setting ex_import_block/ex_import_block FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/ex_import_blockCovermodel.h"
::pct::set_default_encap_config SYSTEM_LIBRARY:ex_import_block/ex_import_block FastBuild
if {[file exists [file normalize [file dirname [info script]]]/ex_import_block_import_user_post.tcl]} { source [file normalize [file dirname [info script]]]/ex_import_block_import_user_post.tcl }
