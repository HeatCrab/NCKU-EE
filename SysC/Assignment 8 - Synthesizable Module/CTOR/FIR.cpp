#include "FIR.h"

using sc_dt::sc_fixed;

void FIR::initialize() {
  coeffs = new sc_uint<32>[taps + 1];
  buffer = new sc_uint<32>[taps + 1];

  for (int i = 0; i <= taps; ++i) {
    buffer[i] = 0;
  }

  sc_fixed<32, 16> fb = (float)1 / (taps + 1);
  for (int i = 0; i <= taps; ++i) {
    for (int j = 0; j < 32; ++j) {
      coeffs[i][j] = fb[j];
    }
  }
}

void FIR::process_fir() {
  // Reset behavior
  // SystemC kernel handles checking the reset signal automatically
  // due to reset_signal_is()
  for (int i = 0; i <= taps; ++i) {
    buffer[i] = 0;
  }
  y.write(0);

  // Main behavior
  while (true) {
    // Wait for next clock edge
    wait();

    sc_uint<32> result = 0;
    for (int i = taps; i > 0; --i) {
      buffer[i] = buffer[i - 1];
      result += buffer[i] * coeffs[i];
    }
    buffer[0] = x.read();
    result += buffer[0] * coeffs[0];
    y.write(result);
  }
}
