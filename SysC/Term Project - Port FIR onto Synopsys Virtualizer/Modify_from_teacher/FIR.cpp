#include "FIR.h"

void FIR::fir()
{
    /* Reset */
    sum = 0;
    for(int i=0 ; i<32 ; i++){
        mid[i] = 0;
    }

    while(1){
        wait();
        mid[0] = x;
        for(int i=1 ; i<32 ; i++)
            mid[i] = mid[i-1];
        sum = x.read() * b;
        for(int j=0 ; j<32 ; j++)
            sum = sum + (mid[j].read() * b);

        y = sum;
    }
}
