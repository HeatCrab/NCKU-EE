#include "FIR.h"

void FIR::fb_cal()
{
    fb = (float)1/(tap+1);     // get the fixed number of b
    for (int i = 0; i<32; i++) // copy to unsigned 32-bit
       b[i] = fb[i];
    cout << "b of tap " << dec << tap << " is 0x" << hex << b << endl;
}

void FIR::fir()
{
    /* Reset */
    sum = 0;
    for(int i=0 ; i<tap ; i++){
        mid[i] = 0;
    }

    while(1){
        wait();
        mid[0] = x;
        for(int i=1 ; i<tap ; i++)
            mid[i] = mid[i-1];
        sum = x.read() * b;
        for(int j=0 ; j<tap ; j++)
            sum = sum + (mid[j].read() * b);

        y = sum;
    }
}	
