// timer.cpp
#include "timer.h"

void timer::runtimer() {
    // Reset behavior
    cout << "Timer: timer start detected " << endl;
    count = 5;
    timeout.write(0);

    // wait for the first clock edge
    wait(); 

    while(1) {
        if (count == 0) {
            timeout.write(1);
        } else {
            count--;
            timeout.write(0);
        }
        wait();
    }
}

