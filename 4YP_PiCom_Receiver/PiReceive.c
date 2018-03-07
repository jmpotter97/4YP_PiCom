#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)
#include <string.h> // for strlen(string)

const int num_of_ADC = 1;	// CHANGE THIS TO 2 WHEN SECOND ADC IMPLEMENTED (QAM)
const uint clock_pin = 4;
int mask_size;

// ADC_bits is a bit mask of the GPIO pins which that ADC uses, expressed here
// in the form b7,...,b0. This is XOR'd with the gpioWrite_Bits_0_31_Set bit mask
// (which is passed to this program to get the bit mask for gpioWrite_Bits_0_31_Clear 
const uint ADC_1_bits[8] = {5,6,13,19,26,21,20,16};
//const uint ADC_2_bits[8];
int ADC_1_mask = (1<<5)|(1<<6)|(1<<13)|(1<<19)|(1<<26)|(1<<21)|(1<<20)|(1<<16);
//int ADC_2_mask;


// Callback function is automatically passed gpio (will be clock_pin),
// level (0_falling, 1_rising,2_watchdog) and tick (to compare times)
// gpioTick() (uint32_t) gets tick at any time in code, microseconds since boot
void readPins(int gpio, int level, uint tick, void* data) {
	static count = 0;
    int* new_data = (int*)data;
	if(!level){
		*(new_data+count++) = gpioRead_Bits_0_31();
	} else {
        if(count>=mask_size) {
            gpioSetAlertFuncEx(clock_pin, 0, NULL);
        }
    }
	
}

int main(int argc, char *argv[]) {
	// CHANGE SAMPLE RATE OF GPIO's (1,2,4,5,8,10),
	// STANDARD IS 5us (200kHz), FASTEST IS 1us (1MHz)
    // 2us chosen for now
	gpioCfgClock(2,1,0);
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}
    for(int i=0;i<8;i++) {
        gpioSetMode(ADC_1_bits[i], PI_INPUT);
    }


    const int sub_mask_size = 2 * num_of_ADC;
    int* receive_data_mask = calloc(mask_size, sizeof(uint32_t));

	if(argc>1) {
		mask_size = atoi(argv[1]);
	} else {
		printf("PiTransmit_2\n\n");
		printf("Usage: ./PiTransmit_2 mask_size \n");
		return 3;
	}

	/******************************************************************/
	// Using a self-generated clock FOR TESTING
	gpioHardwareClock(clock_pin, 5000);
	gpioSetAlertFuncEx(clock_pin, readPins, (void*)receive_data_mask);
	// When testing on scope, sleep for 60s to have enough time to check
	sleep(60);
	gpioHardwareClock(clock_pin, 0);
	/******************************************************************/
	
	gpioTerminate();
	return 0;
}
