#include <stdio.h>
#include <stdlib.h> // for int = atoi(char)
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
	printf("Hello World\n");
	
	int transmit_freq = 2000000;
	// Receive actual transmit frequency from main arguments
	if(argc>1) transmit_freq = atoi(argv[1]);
	
	uint clock_pin = 4;
	gpioHardwareClock(clock_pin, transmit_freq);
	
	gpioTerminate();
}
