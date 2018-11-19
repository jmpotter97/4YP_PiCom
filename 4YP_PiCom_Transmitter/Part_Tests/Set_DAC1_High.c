#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint CLK_PIN = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
	printf("Start\n");
    gpioWrite_Bits_0_31_Set(70852704);
    int secs = 10;
    for(int i=0; i<secs*1000; i++) {
		gpioWrite(CLK_PIN, 0);
		usleep(500);
		gpioWrite(CLK_PIN,1);
		usleep(500);
	}
	gpioWrite_Bits_0_31_Clear(70852704);
	gpioWrite(CLK_PIN, 0);

	gpioTerminate();
	printf("End\n");
	return 0;
}
