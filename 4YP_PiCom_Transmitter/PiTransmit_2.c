#include <stdio.h>
#include <stdlib.h> // for int = atoi(char)
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

void newState() {
	printf("\nHey!");//gpioWrite_Bits_0_31_Clear((1<<17)|(1<<27));
		//usleep(500000/transmit_freq);
		//gpioWrite_Bits_0_31_Set((1<<data0_pin)|(1<<data1_pin));
		//usleep(500000/transmit_freq);
}

int main(int argc, char *argv[]) {
	// REMEMBER TO CHANGE SAMPLE RATE OF GPIO's, STANDARD IS 5us
	// gpioCfgClock()
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
	printf("Hello World\n");

	// argv should have values:
	// argv[1] = size_of_input
	// argv[2] = transmit_data - This is a bit mask for gpioWrite_Bits_0_31_Set
	// argv[3] = 
	
	int transmit_freq = 50000;
	// Receive actual transmit frequency from main arguments
	if(argc>1) transmit_freq = atoi(argv[1]);
	else { printf("GPIO INIT FAIL\n"); return 1;}
	if(argc>2) transmit_freq = atoi(argv[2]);
	
	uint clock_pin = 4;
	uint data0_pin = 17;
	uint data1_pin = 27;
	gpioSetMode(data0_pin, PI_INPUT);
	gpioSetMode(data1_pin, PI_INPUT);
	gpioHardwareClock(clock_pin, transmit_freq);
	gpioSetAlertFunc(clock_pin,newState);
	while(0) {
		
	}
	gpioHardwareClock(clock_pin, 0);
	gpioTerminate();
}
