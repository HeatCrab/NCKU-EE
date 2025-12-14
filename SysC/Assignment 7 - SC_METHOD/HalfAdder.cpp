#include "HalfAdder.h"

void HalfAdder::compute() {
    Sum.write(A.read() ^ B.read());      // Sum is XOR of A and B
    Carry.write(A.read() & B.read());    // Carry is AND of A and B
}