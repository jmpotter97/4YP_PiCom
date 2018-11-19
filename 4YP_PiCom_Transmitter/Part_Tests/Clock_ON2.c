#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint clock_pin = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    gpioHardwareClock(clock_pin,5000);
    getchar();
    gpioHardwareClock(clock_pin,0);
	gpioTerminate();
}
