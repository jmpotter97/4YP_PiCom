#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    int mask = (1<<5)|(1<<6)|(1<<13)|(1<<19)|(1<<26)|(1<<21)|(1<<20)|(1<<16);
    printf("----- Single Pin vs Bank On-Off Write Test -----\n");
    
    printf("\nEMPTY FOR LOOP\n");
    int t0=gpioTick();
	for(int i=0; i<1000; i++) {
		
    }
    int t1 = gpioTick()-t0;
    printf("Time per for loop: %.4fus\nFrequency: %.4fMHz\n",
				(float)t1/(1000),(float)(1000)/t1);
				
	printf("\nSINGLE TRANSITION\n");
    t0=gpioTick();
	for(int i=0; i<1000; i++) {
        gpioWrite(clock_pin,0);
        gpioWrite(clock_pin,1);
    }
    t1 = gpioTick()-t0;
    printf("Time per for loop (on, off): %.4fus\nPer-Write Frequency: %.4fMHz\n",
				(float)t1/(1000),(float)(2000)/t1);
    
    printf("\nBANK TRANSITION\n");
    t0=gpioTick();
	for(int i=0; i<1000; i++) {
		// A CLEAR AND A SET IS REQUIRED FOR A PROPER WRITE OF VALUES
		// SO THIS REPLICATES THE FUNCTION ABOVE
        gpioWrite_Bits_0_31_Clear(mask);
        gpioWrite_Bits_0_31_Set(0);
        gpioWrite_Bits_0_31_Clear(0);
        gpioWrite_Bits_0_31_Set(mask);
    }
    t1 = gpioTick()-t0;
    printf("Time per for loop (all on, all off): %.4fus\nPer-Write Frequency: %.4fMHz\n",
				(float)t1/(1000),(float)(2000)/t1);

	gpioTerminate();
}
