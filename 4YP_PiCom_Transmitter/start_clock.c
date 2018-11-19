#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}


	/*  argv should have values:
		argv[1] = transmit_freq - Frequency of clock signal, or take default:
	*/	int transmit_freq = 5000;
	
	if(argc>1) {
		transmit_freq = atoi(argv[1]);
	} else {
		printf("start_clock\n\n");
		printf("Usage: ./start_clock transmit_freq\n");
		return 1;
	}
	
	gpioHardwareClock(clock_pin, transmit_freq);
	gpioTerminate();
}
