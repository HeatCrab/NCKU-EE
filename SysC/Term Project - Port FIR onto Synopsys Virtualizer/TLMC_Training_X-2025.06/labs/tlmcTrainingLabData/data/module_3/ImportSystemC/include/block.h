#ifndef BLOCK_H
#define BLOCK_H
#include <scml.h>
#include <scml2.h>

template<typename Ttn, bool Tb, int Tint>
class ex_import_block : public sc_module {
public:
  sc_in<bool> in;
  tlm::tlm_target_socket<32> socket;
  sc_core::sc_in<bool> p_reset;
  sc_core::sc_in<bool> p_clk;

  SC_HAS_PROCESS(ex_import_block);

  ex_import_block(const sc_module_name& name
      , int ca_int
      , bool ca_bool
      , double ca_double = 0.0 
      , std::string ca_string = "any"
      ) : 
    sc_module(name)
    , in("in")
    , socket("socket")
    , p_reset("p_reset")
    , p_clk("p_clk")
    , m_ui("p_uint", 2)
    , m_b("p_bool", true) 
    , m_d("p_double", 3.14) 
    , m_s("p_string", "one")
    , MemoryMap("MemoryMap", (12) / scml2::sizeOf<unsigned int >())
  {
    sensitive<<in;
    SC_METHOD(init);

    /* initialize adapter */
    socket_adapter = scml2::target_port_adaptor::create("socket_adapter", &socket);
    /* bind FT adapter to memory */
    (*socket_adapter)(MemoryMap);

  }

  void init() {
    std::cout<<"Puint,"<<m_ui.getUIntValue()<<std::endl;
    std::cout<<"Pbool,"<<m_b.getBoolValue()<<std::endl;
    std::cout<<"Pdouble,"<<m_d.getDoubleValue()<<std::endl;
    std::cout<<"Pstring,"<<m_s.getStringValue()<<std::endl;
    std::cout<<"Ttn,"<<(Ttn)(5.3)<<std::endl;
    std::cout<<"Tb,"<< Tb <<std::endl;
    std::cout<<"Tint,"<<Tint<<std::endl;
  }

  scml_property<unsigned int> m_ui;
  scml_property<bool> m_b;
  scml_property<double> m_d;
  scml_property<std::string> m_s;

  scml2::memory< unsigned int > MemoryMap;
  scml2::target_port_adaptor* socket_adapter;
};

#endif /* BLOCK_H */
