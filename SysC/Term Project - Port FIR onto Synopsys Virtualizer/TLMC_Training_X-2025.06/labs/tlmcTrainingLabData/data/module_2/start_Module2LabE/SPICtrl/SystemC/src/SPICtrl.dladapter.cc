#include "SystemC/include/RX_PATH.h"
#include "SystemC/include/RX_PATHBase.h"
#include "SystemC/include/SPICtrl.h"
#include "SystemC/include/SPICtrlCovermodel.h"
#include "SystemC/include/TX_PATH.h"
#include "SystemC/include/TX_PATHBase.h"
#include "tlm.h"
#include "tlm_ft_spi.h"
#include "cassert"
#include "cwr_dynamic_loader.h"
#include "cwr_sc_dynamic_stubs.h"
#include "cwr_sc_hierarch_module.h"
#include "cwr_sc_object_creator.h"
#include "scmlinc/scml_abstraction_level_switch.h"
#include "scmlinc/scml_property_registry.h"

namespace SPICtrl_SPICtrl_FastBuild {

using namespace conf;
using namespace std;


class SPICtrlPctWrapper : public SPICtrl, public conf::component_helper_wrapper_base
{
private:
  ::SPICtrlCovermodel* _SPICtrlCovermodel;

public:
  SPICtrlPctWrapper(sc_module_name _name_)
    : SPICtrl(_name_)
    , _SPICtrlCovermodel(this->createHelper<::SPICtrlCovermodel, SPICtrlPctWrapper >("coverage", this))
  {}
  virtual ~SPICtrlPctWrapper() {
    delete _SPICtrlCovermodel;
  }
};


class SPICtrl0Creator : public ScObjectCreatorBase
{
public:
  static unsigned int creationVerboseMode() {
    const char * const env_var_val = ::getenv("SNPS_SLS_DYNAMIC_CREATION_VERBOSE");
    return env_var_val ? (::atoi(env_var_val)) : 3;
  }
  sc_object* create ( const string& name ) {
    string hierach_name = getHierarchicalName(name);
    if (::getenv("SNPS_VP_PRINT_PROPERTIES_FOR") != nullptr && hierach_name == ::getenv("SNPS_VP_PRINT_PROPERTIES_FOR")) scml_property_registry::inst().printPropertiesFor(hierach_name);
    if (scml_property_registry::inst().hasProperty(scml_property_registry::MODULE, scml_property_registry::BOOL, hierach_name, "runtime_disabled") && 
        scml_property_registry::inst().getBoolProperty(scml_property_registry::MODULE, hierach_name, "runtime_disabled")) {
      sc_module_name n(name.c_str());
      if (creationVerboseMode() >= 6) { std::cout << "SPICtrl/SPICtrl: STUB for " << hierach_name << " created (1.0)." << std::endl; }
      conf::stub *result = new conf::stub(n);
      registerStubPorts(result, name);
      return result;
    } else {
      if (creationVerboseMode() >= 3) { std::cout << "SPICtrl/SPICtrl: " << hierach_name << " created (1.0)." << std::endl; }
      SPICtrlPctWrapper* result = new SPICtrlPctWrapper(name.c_str());
      registerPorts(result, name);
      return result;
    }
  }
  void registerPorts(SPICtrlPctWrapper* result, const string& name) {
    string hierach_name = getHierarchicalName(name);
    cwr_sc_object_registry::inst().addTargetSocket(&result->bus_reg_in, string(static_cast<sc_object*>(result)->name()) + ".bus_reg_in" );
    cwr_sc_object_registry::inst().addInitiatorSocket(&result->Serial_IO, string(static_cast<sc_object*>(result)->name()) + ".Serial_IO" );
    cwr_sc_object_registry::inst().addPort(&result->rst_in, string(static_cast<sc_object*>(result)->name()) + ".rst_in" );
    cwr_sc_object_registry::inst().addPort(&result->spi_clk, string(static_cast<sc_object*>(result)->name()) + ".spi_clk" );
    cwr_sc_object_registry::inst().addPort(&result->clk_in, string(static_cast<sc_object*>(result)->name()) + ".clk_in" );
    cwr_sc_object_registry::inst().addPort(&result->tfuf_irq, string(static_cast<sc_object*>(result)->name()) + ".tfuf_irq" );
    cwr_sc_object_registry::inst().addPort(&result->tfff_irq, string(static_cast<sc_object*>(result)->name()) + ".tfff_irq" );
    cwr_sc_object_registry::inst().addPort(&result->rfof_irq, string(static_cast<sc_object*>(result)->name()) + ".rfof_irq" );
    cwr_sc_object_registry::inst().addPort(&result->rfdf_irq, string(static_cast<sc_object*>(result)->name()) + ".rfdf_irq" );
  }
  void registerStubPorts(conf::stub* result, const string& name) {
    string hierach_name = getHierarchicalName(name);
    cwr_sc_object_registry::inst().addTargetSocket(new conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>(std::string("bus_reg_in" ).c_str()), string(static_cast<sc_object*>(result)->name()) + ".bus_reg_in" );
    cwr_sc_object_registry::inst().addInitiatorSocket(new tlm_ft_spi_device_socket_stub(std::string("Serial_IO" ).c_str()), string(static_cast<sc_object*>(result)->name()) + ".Serial_IO" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::rst_in, "rst_in" , string(static_cast<sc_object*>(result)->name()) + ".rst_in" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::spi_clk, "spi_clk" , string(static_cast<sc_object*>(result)->name()) + ".spi_clk" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::clk_in, "clk_in" , string(static_cast<sc_object*>(result)->name()) + ".clk_in" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::tfuf_irq, "tfuf_irq" , string(static_cast<sc_object*>(result)->name()) + ".tfuf_irq" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::tfff_irq, "tfff_irq" , string(static_cast<sc_object*>(result)->name()) + ".tfff_irq" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::rfof_irq, "rfof_irq" , string(static_cast<sc_object*>(result)->name()) + ".rfof_irq" );
    conf::stub_port_registrator<>::register_stub_port(&SPICtrl::rfdf_irq, "rfdf_irq" , string(static_cast<sc_object*>(result)->name()) + ".rfdf_irq" );
  }
};



struct DllAdapter {
  DllAdapter() {
    ScInitiatorSocketFactory::inst().addCreator ("conf::tlm_initiator_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScInitiatorSocketCreator<conf::tlm_initiator_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScInitiatorSocketFactory::inst().addCreator ("scml2::tlm_serial_device_socket<scml2::FULL_DUPLEX, FtSpiProtocol, 1>", new ScInitiatorSocketCreator<scml2::tlm_serial_device_socket<scml2::FULL_DUPLEX, FtSpiProtocol, 1> >());
    ScInitiatorSocketFactory::inst().addCreator ("tlm::tlm_base_initiator_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScInitiatorSocketCreator<tlm::tlm_base_initiator_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScInitiatorSocketFactory::inst().addCreator ("tlm_ft_spi_device_socket_stub", new ScInitiatorSocketCreator<tlm_ft_spi_device_socket_stub>());
    ScObjectFactory::inst().addCreator ("SPICtrl0", new SPICtrl0Creator());
    ScObjectFactory::inst().addCreator ("sc_signal<bool>", new ScPrimChannelCreator<sc_signal<bool> >());
    ScPortFactory::inst().addCreator ("sc_in<bool>", new ScPortCreator<sc_in<bool> >());
    ScPortFactory::inst().addCreator ("sc_inout<bool>", new ScPortCreator<sc_inout<bool> >());
    ScPortFactory::inst().addCreator ("sc_out<bool>", new ScPortCreator<sc_out<bool> >());
    ScTargetSocketFactory::inst().addCreator ("conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScTargetSocketCreator<conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScTargetSocketFactory::inst().addCreator ("scml2::tlm_serial_bus_socket<scml2::FULL_DUPLEX, FtSpiProtocol, 0>", new ScTargetSocketCreator<scml2::tlm_serial_bus_socket<scml2::FULL_DUPLEX, FtSpiProtocol, 0> >());
    ScTargetSocketFactory::inst().addCreator ("tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScTargetSocketCreator<tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScTargetSocketFactory::inst().addCreator ("tlm_ft_spi_bus_socket_stub", new ScTargetSocketCreator<tlm_ft_spi_bus_socket_stub>());
    if (::getenv("SNPS_SLS_DYNAMIC_LOADER_VERBOSE")) { std::cout << "SPICtrl/SPICtrl (1.0) loaded. Build timestamp: " << __DATE__ << " " << __TIME__ << std::endl; }
  }
  ~DllAdapter() {
  }
  static DllAdapter sInstance;
};

DllAdapter DllAdapter::sInstance;

}
