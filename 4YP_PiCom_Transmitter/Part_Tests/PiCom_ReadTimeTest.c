#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    printf("----- Single Pin vs Bank Read Test -----\n");
    
	printf("\nSINGLE READ\n");
	uint single;
    int t0=gpioTick();
	for(int i=0; i<1000; i++) {
        single = gpioRead(clock_pin);
    }
    int t1 = gpioTick()-t0;
    printf("Time per for loop (single read): %.4fus\nRead Frequency: %.4fMHz\n",
				(float)t1/(1000),(float)(1000)/t1);
    
    printf("\nBANK READ\n");
    uint32_t bank;
    t0=gpioTick();
	for(int i=0; i<1000; i++) {
		bank = gpioRead_Bits_0_31();
    }
    t1 = gpioTick()-t0;
    printf("Time per for loop (bank read): %.4fus\nRead Frequency: %.4fMHz\n",
				(float)t1/(1000),(float)(1000)/t1);
	printf("\n%i",(single+bank)*0);
	gpioTerminate();
}
