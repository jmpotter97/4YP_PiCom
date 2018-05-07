#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

const uint CLK_PIN = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
    gpioHardwareClock(CLK_PIN, 5000);
    getchar();
	gpioHardwareClock(CLK_PIN, 0);
	gpioTerminate();
}
