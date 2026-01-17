#include "/home/user1/sc25/sc2568/TLMCreation_Quickstart_Training_X-2025.06/TLMC_Training_X-2025.06/labs/tlmcTrainingLabData/tlmcTrainingLabData/data/module_3/ImportSystemC/include/block.h"
#include "SystemC/include/ex_import_blockCovermodel.h"
#include "cassert"
#include "cwr_dynamic_loader.h"
#include "cwr_sc_dynamic_stubs.h"
#include "cwr_sc_hierarch_module.h"
#include "cwr_sc_object_creator.h"
#include "scmlinc/scml_abstraction_level_switch.h"
#include "scmlinc/scml_property_registry.h"

namespace ex_import_block_ex_import_block_FastBuild {

using namespace conf;
using namespace std;

template<typename Ttn, bool Tb, int Tint>
class ex_import_blockPctWrapper : public ex_import_block<Ttn, Tb, Tint>, public conf::component_helper_wrapper_base
{
private:
  ::ex_import_blockCovermodel<Ttn, Tb, Tint>* _ex_import_blockCovermodel;

public:
  ex_import_blockPctWrapper(sc_module_name _name_, int ca_int, bool ca_bool, double ca_double, string ca_string)
    : ex_import_block<Ttn, Tb, Tint>(_name_, ca_int, ca_bool, ca_double, ca_string.c_str())
    , _ex_import_blockCovermodel(this->createHelper<::ex_import_blockCovermodel<Ttn, Tb, Tint>, ex_import_blockPctWrapper >("coverage", this))
  {}
  virtual ~ex_import_blockPctWrapper() {
    delete _ex_import_blockCovermodel;
  }
};

template<typename Ttn, bool Tb, int Tint>
class ex_import_block0Creator : public ScObjectCreatorBase
{
public:
  static unsigned int creationVerboseMode() {
    const char * const env_var_val = ::getenv("SNPS_SLS_DYNAMIC_CREATION_VERBOSE");
    return env_var_val ? (::atoi(env_var_val)) : 3;
  }
  sc_object* create ( const string& name ) {
    string hierach_name = getHierarchicalName(name);
    int ca_int = scml_property_registry::inst().getIntProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_int");

    bool ca_bool = scml_property_registry::inst().getBoolProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_bool");

    double ca_double = scml_property_registry::inst().getDoubleProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_double");

    string ca_string = scml_property_registry::inst().getStringProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_string");

    if (::getenv("SNPS_VP_PRINT_PROPERTIES_FOR") != nullptr && hierach_name == ::getenv("SNPS_VP_PRINT_PROPERTIES_FOR")) scml_property_registry::inst().printPropertiesFor(hierach_name);
    if (scml_property_registry::inst().hasProperty(scml_property_registry::MODULE, scml_property_registry::BOOL, hierach_name, "runtime_disabled") && 
        scml_property_registry::inst().getBoolProperty(scml_property_registry::MODULE, hierach_name, "runtime_disabled")) {
      sc_module_name n(name.c_str());
      if (creationVerboseMode() >= 6) { std::cout << "ex_import_block/ex_import_block: STUB for " << hierach_name << " created." << std::endl; }
      conf::stub *result = new conf::stub(n);
      registerStubPorts(result, name);
      return result;
    } else {
      if (creationVerboseMode() >= 6) { std::cout << "ex_import_block/ex_import_block: " << hierach_name << " created." << std::endl; }
      ex_import_blockPctWrapper<Ttn, Tb, Tint>* result = new ex_import_blockPctWrapper<Ttn, Tb, Tint>(name.c_str(), ca_int, ca_bool, ca_double, ca_string.c_str());
      registerPorts(result, name);
      return result;
    }
  }
  void registerPorts(ex_import_blockPctWrapper<Ttn, Tb, Tint>* result, const string& name) {
    string hierach_name = getHierarchicalName(name);
    int ca_int = scml_property_registry::inst().getIntProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_int");

    bool ca_bool = scml_property_registry::inst().getBoolProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_bool");

    double ca_double = scml_property_registry::inst().getDoubleProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_double");

    string ca_string = scml_property_registry::inst().getStringProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_string");

    cwr_sc_object_registry::inst().addPort(&result->in, string(static_cast<sc_object*>(result)->name()) + ".in" );
    cwr_sc_object_registry::inst().addTargetSocket(&result->socket, string(static_cast<sc_object*>(result)->name()) + ".socket" );
    cwr_sc_object_registry::inst().addPort(&result->p_reset, string(static_cast<sc_object*>(result)->name()) + ".p_reset" );
    cwr_sc_object_registry::inst().addPort(&result->p_clk, string(static_cast<sc_object*>(result)->name()) + ".p_clk" );
  }
  void registerStubPorts(conf::stub* result, const string& name) {
    string hierach_name = getHierarchicalName(name);
    int ca_int = scml_property_registry::inst().getIntProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_int");

    bool ca_bool = scml_property_registry::inst().getBoolProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_bool");

    double ca_double = scml_property_registry::inst().getDoubleProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_double");

    string ca_string = scml_property_registry::inst().getStringProperty(
	      scml_property_registry::CONSTRUCTOR, hierach_name, "ca_string");

    conf::stub_port_registrator<>::register_stub_port(&ex_import_block<Ttn, Tb, Tint>::in, "in" , string(static_cast<sc_object*>(result)->name()) + ".in" );
    cwr_sc_object_registry::inst().addTargetSocket(new conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>(std::string("socket" ).c_str()), string(static_cast<sc_object*>(result)->name()) + ".socket" );
    conf::stub_port_registrator<>::register_stub_port(&ex_import_block<Ttn, Tb, Tint>::p_reset, "p_reset" , string(static_cast<sc_object*>(result)->name()) + ".p_reset" );
    conf::stub_port_registrator<>::register_stub_port(&ex_import_block<Ttn, Tb, Tint>::p_clk, "p_clk" , string(static_cast<sc_object*>(result)->name()) + ".p_clk" );
  }
};



struct DllAdapter {
  DllAdapter() {
    ScInitiatorSocketFactory::inst().addCreator ("conf::tlm_initiator_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScInitiatorSocketCreator<conf::tlm_initiator_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScInitiatorSocketFactory::inst().addCreator ("tlm::tlm_base_initiator_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScInitiatorSocketCreator<tlm::tlm_base_initiator_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScObjectFactory::inst().addCreator ("ex_import_block0<int, false, 0>", new ex_import_block0Creator<int, false, 0>());
    ScObjectFactory::inst().addCreator ("ex_import_block0<int, true, 0>", new ex_import_block0Creator<int, true, 0>());
    ScObjectFactory::inst().addCreator ("ex_import_block0<int, true, 1>", new ex_import_block0Creator<int, true, 1>());
    ScObjectFactory::inst().addCreator ("sc_signal<bool>", new ScPrimChannelCreator<sc_signal<bool> >());
    ScPortFactory::inst().addCreator ("sc_in<bool>", new ScPortCreator<sc_in<bool> >());
    ScPortFactory::inst().addCreator ("sc_inout<bool>", new ScPortCreator<sc_inout<bool> >());
    ScPortFactory::inst().addCreator ("sc_out<bool>", new ScPortCreator<sc_out<bool> >());
    ScTargetSocketFactory::inst().addCreator ("conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScTargetSocketCreator<conf::tlm_target_socket_stub<32, tlm::tlm_base_protocol_types, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    ScTargetSocketFactory::inst().addCreator ("tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND>", new ScTargetSocketCreator<tlm::tlm_base_target_socket<32, tlm::tlm_fw_transport_if<tlm::tlm_base_protocol_types>, tlm::tlm_bw_transport_if<tlm::tlm_base_protocol_types>, 1, sc_core::SC_ONE_OR_MORE_BOUND> >());
    if (::getenv("SNPS_SLS_DYNAMIC_LOADER_VERBOSE")) { std::cout << "ex_import_block/ex_import_block loaded. Build timestamp: " << __DATE__ << " " << __TIME__ << std::endl; }
  }
  ~DllAdapter() {
  }
  static DllAdapter sInstance;
};

DllAdapter DllAdapter::sInstance;

}
