//#include "riscv_32i.h"
#include "DMA2.h"
#include "PJ1Bus0.h"
#include "PJ1Bus1.h"
#include "MEM.h"
#include "fakeCPU.h"
#include "fakeUART.h"

SC_MODULE(Top) {
    sc_in<bool>  clk;
    sc_in<bool>  rst;

    //riscv_32i  *rv1, *rv2;
    fakeCPU    *cpu0, *cpu1;
    DMA2       *dma;
    MEM        *ram0, *ram1, *ram2, *ram3;
    UART       *uart0;
    UART       *uart1;
    PJ1Bus0    *bus0;
    PJ1Bus0    *bus1;
    PJ1Bus1    *bus2;

    sc_signal<bool> int0, int1;
    void sysFunc();

    SC_CTOR(Top) {
        // --- 1. Instantiation ---
        //rv1      = new riscv_32i("RV1");
        //rv2      = new riscv_32i("RV2");
        cpu0     = new fakeCPU("CPU0", true);
        cpu1     = new fakeCPU("CPU1", false);
        dma      = new DMA2("DMA", 0x100000);
        ram0     = new MEM("RAM0", 0x100000, 0x00000, 3); 
        ram1     = new MEM("RAM1", 0x100000, 0x00000, 3);
        ram2     = new MEM("RAM2", 0x100000, 0x200000, 3);
        ram3     = new MEM("RAM3", 0x100000, 0x300000, 3);
        uart0    = new UART("UART0", 0x400000);
        uart1    = new UART("UART0", 0x401000);
        
        bus0 = new PJ1Bus0("Bus0");
        bus1 = new PJ1Bus0("BusA");
        bus2 = new PJ1Bus1("Bus2");

        cpu0->clk(clk);
        cpu0->Reset(rst);
        cpu1->clk(clk);
        cpu1->Reset(rst);

        dma->clk(clk);
        dma->RST(rst);

        // --- 2. Hierarchical Socket Binding ---

        // Local Path 0
        //rv1->isock.bind(bus0->Ssocket);
        cpu0->Msocket.bind(bus0->Ssocket);
        bus0->Msocket0.bind(ram0->Ssocket);     // Local RAM0 is index 0
        bus0->Msocket1.bind(bus2->Ssocket0);    // System Bus is index 1
        bus0->clk(clk);
        bus0->rst(rst);

        // Local Path 1
        //rv2->isock.bind(bus1->Ssocket);
        cpu1->Msocket.bind(bus1->Ssocket);
        bus1->Msocket0.bind(ram1->Ssocket);     // Local RAM1 is index 0
        bus1->Msocket1.bind(bus2->Ssocket1);    // System Bus is index 1
        bus1->clk(clk);
        bus1->rst(rst);

        // System Path (Bus 2)
        dma->Msocket0.bind(bus2->Ssocket2);     // DMA Master 0
        dma->Msocket1.bind(bus2->Ssocket3);     // DMA Master 1
        bus2->Msocket0.bind(dma->Ssocket);      // DMA Config Regs is index 0
        bus2->Msocket1.bind(ram2->Ssocket);     // RAM2 is index 1
        bus2->Msocket2.bind(ram3->Ssocket);     // RAM3 is index 2
        bus2->Msocket3.bind(uart0->Ssocket);    // UART0 is index 3
        bus2->Msocket4.bind(uart1->Ssocket);    // UART0 is index 4
        bus2->clk(clk);
        bus2->rst(rst);

        // --- 3. Custom Routing Logic (Manual Address Decoding) ---
        //setup_routing();

        // --- 4. Interrupts ---
        cpu0->Interrupt(int0);
        cpu1->Interrupt(int1);
        dma->INT0(int0); //rv1->int_in(int0);
        dma->INT1(int1); //rv2->int_in(int1);

        SC_CTHREAD(sysFunc, clk.pos());
        reset_signal_is(rst, true);
    }
};

