#include "FullAdder.h"

void FullAdder::compute() {
    Cout.write(ha1_carry.read() | ha2_carry.read());
}