#include "FIR.h"

using sc_dt::sc_fixed;

void FIR::process_fir() {
    // Reset behavior
    for (unsigned int i = 0; i < tap; i++) {
        regs[i] = 0;
        b[i] = 0; // Initialize coefficients to zero
    }
    y.write(0);

    sc_fixed<32, 16> fb;
    sc_uint<32> b_val;

    fb = (float)1 / (tap + 1);

    // Initialize coefficients
    for (int i = 0; i < 32; i ++) {
        b_val[i] = fb[i];
    }

    // Set all coefficients to b matrix
    for (unsigned int i = 0; i < tap; i++) {
        b[i] = b_val;
    }

    wait();

    while (true) {
        sc_uint<32> x_val = x.read();

        // Shift registers
        for (unsigned int i = tap - 1; i > 0; i--) {
            regs[i] = regs[i - 1]; 
        }
        regs[0] = x_val;

        // FIR computation
        sc_fixed<32, 16> acc = 0;
        sc_fixed<32, 16> val_data;
        sc_fixed<32, 16> val_coeff;

        for (unsigned int i = 0; i < tap; i++) {
            // Copy coefficient bit-by-bit
            for (int j = 0; j < 32; j++) {
                val_coeff[j] = b[i][j];
            }
            // Copy data bit-by-bit
            for (int j = 0; j < 32; j++) {
                val_data[j] = regs[i][j];
            }
            acc += val_data * val_coeff;
        }

        // Copy result bit-by-bit to output
        sc_uint<32> y_val;
        for (int i = 0; i < 32; i++) {
            y_val[i] = acc[i];
        }
        y.write(y_val);
        wait();
    }

}