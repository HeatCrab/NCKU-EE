//#include "riscv_32i.h"
#include "Top.h"

void Top::sysFunc() {
    // No reset behavior for the system
    while (1) {
        wait();
        // Top is a system containing CPUs and need no behavior here    
    }
}
