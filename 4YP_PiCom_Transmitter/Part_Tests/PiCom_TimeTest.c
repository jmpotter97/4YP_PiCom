#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    int mask = (1<<27)|(1<<5)|(1<<6)|(1<<12);
    int t0=gpioTick();
	for(int i=0; i<1000; i++) {
        gpioWrite_Bits_0_31_Clear(mask);
        gpioWrite_Bits_0_31_Set(mask);
    }
    int t1 = gpioTick()-t0;
    printf("Time per transition: %d\nFrequency: %d\n",t1/2000,2000/t1);

	gpioTerminate();
}
