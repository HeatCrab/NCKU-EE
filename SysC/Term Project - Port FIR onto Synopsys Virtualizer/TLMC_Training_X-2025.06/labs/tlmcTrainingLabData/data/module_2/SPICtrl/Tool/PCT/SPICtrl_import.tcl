#############################################################################
# Copyright 1996-2024 Synopsys, Inc.                                        #
#                                                                           #
# This Synopsys software and all associated documentation are proprietary   #
# to Synopsys, Inc. and may only be used pursuant to the terms and          #
# conditions of a written license agreement with Synopsys, Inc.             #
# All other use, reproduction, modification, or distribution of the         #
# Synopsys software or the associated documentation is strictly prohibited. #
#############################################################################

if {[file exists [file normalize [file dirname [info script]]]/SPICtrl_import_user_pre.tcl]} { source [file normalize [file dirname [info script]]]/SPICtrl_import_user_pre.tcl }
::pct::create_block SPICtrl
::pct::add_generator SPICtrl parameter_change_cb ::SPICtrl::handle_parameter_changed "[file normalize [file dirname [info script]]]/SPICtrl_callback.tcl" 100 parameter_change false false
::pct::add_generator SPICtrl instantiate_cb ::SPICtrl::handle_block_instantiated "[file normalize [file dirname [info script]]]/SPICtrl_callback.tcl" 100 instantiate
::pct::create_encap SPICtrl SPICtrl
::pct::add_encap_header SPICtrl/SPICtrl "[file normalize [file dirname [info script]]]/../../SystemC/include/SPICtrl.h"
::pct::add_encap_source_file SPICtrl/SPICtrl "[file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrl.cc"
::pct::add_to_encap_include_path SPICtrl/SPICtrl "[file normalize [file dirname [info script]]]/../../SystemC/include"
::pct::create_encap_constructor SPICtrl/SPICtrl
::pct::set_default_constructor SPICtrl/SPICtrl SPICtrl()
::pct::set_documentation_url SPICtrl "[file normalize [file dirname [info script]]]/../../Documentation/SPICtrl.html"
::pct::set_documentation_url SPICtrl/SPICtrl "[file normalize [file dirname [info script]]]/../../Documentation/SPICtrl.html"
::pct::set_encap_version SPICtrl/SPICtrl 1.0
::pct::create_scml_property SPICtrl/SPICtrl enable_check_clocks boolean
::pct::set_description SPICtrl/SPICtrl "Scml Properties" enable_check_clocks "Enable/disable the check on the SPI clock communication"
::pct::set_scml_property_property SPICtrl/SPICtrl enable_check_clocks default_value false
::pct::set_param_visibility SPICtrl/SPICtrl "Scml Properties" enable_check_clocks visible
::pct::set_param_editability SPICtrl/SPICtrl "Scml Properties" enable_check_clocks until_simulation_start
::pct::set_param_sweepable SPICtrl/SPICtrl "Scml Properties" enable_check_clocks true
::pct::create_scml_property SPICtrl/SPICtrl target_id integer
::pct::set_description SPICtrl/SPICtrl "Scml Properties" target_id "Identify SPI when in input mode"
::pct::set_scml_property_property SPICtrl/SPICtrl target_id allowed_range_min 0
::pct::set_scml_property_property SPICtrl/SPICtrl target_id allowed_range_max 4294967295
::pct::set_scml_property_property SPICtrl/SPICtrl target_id default_value 0
::pct::set_param_visibility SPICtrl/SPICtrl "Scml Properties" target_id visible
::pct::set_param_editability SPICtrl/SPICtrl "Scml Properties" target_id until_simulation_start
::pct::set_param_sweepable SPICtrl/SPICtrl "Scml Properties" target_id true
::pct::create_scml_property SPICtrl/SPICtrl fifo_size integer
::pct::set_description SPICtrl/SPICtrl "Scml Properties" fifo_size "Size of the internal FIFOs"
::pct::set_scml_property_property SPICtrl/SPICtrl fifo_size allowed_range_min 0
::pct::set_scml_property_property SPICtrl/SPICtrl fifo_size allowed_range_max 4294967295
::pct::set_scml_property_property SPICtrl/SPICtrl fifo_size default_value 5
::pct::set_param_visibility SPICtrl/SPICtrl "Scml Properties" fifo_size visible
::pct::set_param_editability SPICtrl/SPICtrl "Scml Properties" fifo_size until_simulation_start
::pct::set_param_sweepable SPICtrl/SPICtrl "Scml Properties" fifo_size true
::pct::create_scml_property SPICtrl/SPICtrl version integer
::pct::set_scml_property_property SPICtrl/SPICtrl version allowed_values {10003 10200}
::pct::set_scml_property_property SPICtrl/SPICtrl version default_value 10003
::pct::set_param_visibility SPICtrl/SPICtrl "Scml Properties" version hidden
::pct::set_param_editability SPICtrl/SPICtrl "Scml Properties" version until_simulation_start
::pct::set_param_sweepable SPICtrl/SPICtrl "Scml Properties" version true
if {![::pct::is_library_open TLM2_PROTOCOLS]} {
    ::pct::open_library TLM2_PROTOCOLS
}
::pct::create_tlm_encap_port SPICtrl/SPICtrl bus_reg_in "tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types >, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types >, 1, sc_core::SC_ONE_OR_MORE_BOUND>" TARGET_SOCKET REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl bus_reg_in None
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/bus_reg_in TLM2_PROTOCOLS:tlm2_gp
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/bus_reg_in "Port Properties" MasterSlaveness Slave
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/bus_reg_in bus_reg_in
::pct::add_target_location SYSTEM_LIBRARY:SPICtrl/bus_reg_in mRegs
::pct::set_target_location_type SYSTEM_LIBRARY:SPICtrl/bus_reg_in:mRegs block
::pct::set_target_location_size SYSTEM_LIBRARY:SPICtrl/bus_reg_in:mRegs 0x24
::pct::set_target_location_address SYSTEM_LIBRARY:SPICtrl/bus_reg_in:mRegs 0 0x0

if {![::pct::is_library_open tlm_ft_spi_bus]} {
    ::pct::open_library tlm_ft_spi_bus
}
::pct::tlm_ft_spi_protocol::create_device_socket SYSTEM_LIBRARY:SPICtrl SPICtrl Serial_IO ""

::pct::create_bca_encap_port SPICtrl/SPICtrl rst_in bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl rst_in in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/rst_in SYSTEM_LIBRARY:RESET
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/rst_in rst_in pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/rst_in "Port Properties" MasterSlaveness Slave
::pct::RESET::upgrade_port SPICtrl/SPICtrl rst_in false
::pct::create_bca_encap_port SPICtrl/SPICtrl spi_clk bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl spi_clk in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/spi_clk SYSTEM_LIBRARY:CLOCK
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/spi_clk spi_clk pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/spi_clk "Port Properties" MasterSlaveness Slave
::pct::CLOCK::upgrade_port SPICtrl/SPICtrl spi_clk
::pct::create_bca_encap_port SPICtrl/SPICtrl clk_in bool in REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl clk_in in
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/clk_in SYSTEM_LIBRARY:CLOCK
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/clk_in clk_in pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/clk_in "Port Properties" MasterSlaveness Slave
::pct::CLOCK::upgrade_port SPICtrl/SPICtrl clk_in
::pct::create_bca_encap_port SPICtrl/SPICtrl tfuf_irq bool out REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl tfuf_irq out
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/tfuf_irq SYSTEM_LIBRARY:Default
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/tfuf_irq tfuf_irq pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/tfuf_irq "Port Properties" MasterSlaveness Master
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/tfuf_irq:SPICtrl "Protocol Common Parameters" data_width bitwidth(bool)
::pct::interrupt_signal::upgrade_port SPICtrl/SPICtrl tfuf_irq false "" false
::pct::create_bca_encap_port SPICtrl/SPICtrl tfff_irq bool out REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl tfff_irq out
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/tfff_irq SYSTEM_LIBRARY:Default
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/tfff_irq tfff_irq pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/tfff_irq "Port Properties" MasterSlaveness Master
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/tfff_irq:SPICtrl "Protocol Common Parameters" data_width bitwidth(bool)
::pct::interrupt_signal::upgrade_port SPICtrl/SPICtrl tfff_irq false "" false
::pct::create_bca_encap_port SPICtrl/SPICtrl rfof_irq bool out REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl rfof_irq out
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/rfof_irq SYSTEM_LIBRARY:Default
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/rfof_irq rfof_irq pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/rfof_irq "Port Properties" MasterSlaveness Master
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/rfof_irq:SPICtrl "Protocol Common Parameters" data_width bitwidth(bool)
::pct::interrupt_signal::upgrade_port SPICtrl/SPICtrl rfof_irq false "" false
::pct::create_bca_encap_port SPICtrl/SPICtrl rfdf_irq bool out REGULAR_PORT
::pct::add_block_port SYSTEM_LIBRARY:SPICtrl rfdf_irq out
::pct::set_block_port_protocol --set-category SYSTEM_LIBRARY:SPICtrl/rfdf_irq SYSTEM_LIBRARY:Default
::pct::map_encap_port SYSTEM_LIBRARY:SPICtrl/SPICtrl/rfdf_irq rfdf_irq pin
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/rfdf_irq "Port Properties" MasterSlaveness Master
::pct::set_param_value SYSTEM_LIBRARY:SPICtrl/rfdf_irq:SPICtrl "Protocol Common Parameters" data_width bitwidth(bool)
::pct::interrupt_signal::upgrade_port SPICtrl/SPICtrl rfdf_irq false "" false
::pct::create_encap_config SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild
::pct::set_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build enabled true
::pct::set_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build debug true
::pct::set_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build optimized false
::pct::set_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build assertions false
::pct::set_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build dynamic_library true
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build target SPICtrl *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build target_directory "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrl.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/TX_PATH.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/RX_PATH.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrlBase.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build source_file "[file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrl.dladapter.cc" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/SPICtrl.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/TX_PATH.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/TX_PATHBase.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/RX_PATH.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/RX_PATHBase.h" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path "[file normalize [file dirname [info script]]]/../.." *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path "[file normalize [file dirname [info script]]]/../../SystemC/include" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/tlmcreator/templates/models/common/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/common/include/scml2_protocol_engines/tlm2_ft_target_port/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/common/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/common/include/tlm *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/common/include/scml2_protocol_engines/tlm2_ft_initiator_port/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/common/include/tlm_serial *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_can_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_spi_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build include_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_lin_bus/SystemC/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build compile_flag "-fvisibility=hidden" gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build compile_flag -fprofile-arcs gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build compile_flag -ftest-coverage gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build library_path #(SNPS_VP_HOME)#/../../IP/tlm_ft_spi_bus/SystemC/lib-%(COMPILER)% *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build library tlm_ft_spi_bus *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build link_flag -fPIC gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build link_flag -Wl,--no-undefined gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build link_flag -fprofile-arcs gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build link_flag -ftest-coverage gcc-*
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build define SC_INCLUDE_DYNAMIC_PROCESSES "" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild build define DEBUG "" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package dynamic_load SPICtrl %(EXPORTHOME)%/simulation/FastBuild/ *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package dynamic_load SPICtrl "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package define SC_INCLUDE_DYNAMIC_PROCESSES "" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package include_path "[file normalize [file dirname [info script]]]/../.." *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package include_path "[file normalize [file dirname [info script]]]/../../SystemC/include" *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package include_path #(SNPS_VP_HOME)#/tlmcreator/templates/models/common/include *
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/SPICtrl.dll" simulation/FastBuild/ msvc-14.34-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/SPICtrl.dll" simulation/FastBuild/ msvc-14.38-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/libSPICtrl.so" simulation/FastBuild/ gcc-9.5-64
::pct::add_encap_config_setting SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild package package_file "[file normalize [file dirname [info script]]]/../../SystemC/libso-%(COMPILER)%/FastBuild/libSPICtrl.so" simulation/FastBuild/ gcc-12.3-64
if {[file exists [file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrl.rc]} {
::pct::add_encap_config_setting SPICtrl/SPICtrl FastBuild build resource_file "[file normalize [file dirname [info script]]]/../../SystemC/src/SPICtrl.rc"
}
::pct::add_encap_config_setting SPICtrl/SPICtrl FastBuild build component_helper coverage ::SPICtrlCovermodel
::pct::add_encap_config_setting SPICtrl/SPICtrl FastBuild build header_file "[file normalize [file dirname [info script]]]/../../SystemC/include/SPICtrlCovermodel.h"
::pct::set_default_encap_config SYSTEM_LIBRARY:SPICtrl/SPICtrl FastBuild
if {[file exists [file normalize [file dirname [info script]]]/SPICtrl_import_user_post.tcl]} { source [file normalize [file dirname [info script]]]/SPICtrl_import_user_post.tcl }
