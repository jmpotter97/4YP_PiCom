#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    int mask = (1<<13)|(1<<5)|(1<<6)|(1<<19);
    int t0=gpioTick();
	for(int i=0; i<1000; i++) {
        gpioWrite_Bits_0_31_Clear(mask);
        gpioWrite_Bits_0_31_Set(mask);
    }
    int t1 = gpioTick()-t0;
    printf("BANK TRANSITION\n");
    printf("Time per transition: %fus\nFrequency: %fHz\n",
				(float)t1/(2000),(float)(1000*1000000)/t1);
    
    t0=gpioTick();
	for(int i=0; i<1000; i++) {
        gpioWrite(clock_pin,0);
        gpioWrite(clock_pin,1);
    }
    t1 = gpioTick()-t0;
    printf("SINGLE TRANSITION\n");
    printf("Time per transition: %fus\nFrequency: %fHz\n",
				(float)t1/(2000),(float)(1000*1000000)/t1);

	gpioTerminate();
}
