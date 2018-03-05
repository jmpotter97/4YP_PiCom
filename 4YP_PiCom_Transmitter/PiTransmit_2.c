#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)
#include <string.h> // for strlen(string)

const int num_of_DAC = 1;	// CHANGE THIS TO 2 WHEN SECOND DAC IMPLEMENTED (QAM)
const uint clock_pin = 4;

// DAC_bits is a bit mask of the GPIO pins which that DAC uses, expressed here
// in the form b7,...,b0. This is XOR'd with the gpioWrite_Bits_0_31_Set bit mask
// (which is passed to this program to get the bit mask for gpioWrite_Bits_0_31_Clear 
const uint DAC_1_bits[8] = {5,6,13,19,26,21,20,16};
//const uint DAC_2_bits[8];
int DAC_1_mask = (1<<5)|(1<<6)|(1<<13)|(1<<19)|(1<<26)|(1<<21)|(1<<20)|(1<<16);
//int DAC_2_mask;


// Callback function is automatically passed gpio (will be clock_pin),
// level (0_falling, 1_rising,2_watchdog) and tick (to compare times)
// gpioTick() (uint32_t) gets tick at any time in code, microseconds since boot
void newState(uint32_t* mask) {
	/*	TEST VERSION
	if(z++%2<1){
		gpioWrite_Bits_0_31_Clear(DAC_1_mask);
		gpioWrite_Bits_0_31_Set(0);
	} else {
		gpioWrite_Bits_0_31_Clear(0);
		gpioWrite_Bits_0_31_Set(DAC_1_mask);
	}*/

	//	REAL VERSION
	//  Removed from function
	
}

int main(int argc, char *argv[]) {
	// CHANGE SAMPLE RATE OF GPIO's (1,2,4,5,8,10),
	// STANDARD IS 5us (200kHz), FASTEST IS 1us (1MHz)
	//gpioCfgClock(2,1,0);
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}

	/*  argv should have values:
	    argv[1] = transmit_data - This is a sub-bit-mask of DAC pins only,
								  passed as a char*
		argv[2] = transmit_freq - Frequency of clock signal, or take default:
	*/
	//int transmit_freq = 5000;
	char* transmit_data;
	
	if(argc>1) {
		transmit_data = argv[1];
	} else {
		printf("PiTransmit_2\n\n");
		printf("Usage: ./PiTransmit_2 transmit_data \n");
		return 3;
	}
	//if(argc>2) transmit_freq = atoi(argv[2]);
	

	const int sub_mask_size = 2 * num_of_DAC;
	const int mask_size = strlen(transmit_data) / sub_mask_size;
    char format[] = "%_x";			// %2x for one DAC, %4x for two DAC's
    format[1] = sub_mask_size + 48;	// +48 for ASCII value of number

	uint32_t* transmit_data_mask = calloc(mask_size, sizeof(uint32_t));
	for(int i = 0; i<mask_size; i++) {
		// Move each sub-mask into an int in transmit_data_mask array
		sscanf((transmit_data + sub_mask_size*i),format,&transmit_data_mask[i]);
		// Expand sub-mask into 32-bit mask
		// transmit_data_mask[i] = F(transmit_data_mask[i]);
		// WHERE F() MAPS THE 8-BIT SUB-MASK TO THE 32-BIT MASK
		int mask32 = 0;
		for(int j = 0; j<8; j++) {	// TODO: ADD ANOTHER FOR SECOND DAC
			// If each bit in binary exists, include it in 32-bit mask
			if((1<<(7-j)) & transmit_data_mask[i]) {
				mask32 |= (1<<DAC_1_bits[j]);
			}
		}
		transmit_data_mask[i] = mask32;
	}
	
	for(int i=0;i<8;i++) {
		gpioSetMode(DAC_1_bits[i], PI_OUTPUT);
	}
	
	uint32_t t0 = gpioTick();
	for(int i=0; i<mask_size; i++) {
		gpioWrite_Bits_0_31_Clear(transmit_data_mask[i] ^ DAC_1_mask);
		gpioWrite_Bits_0_31_Set(transmit_data_mask[i]);
		//usleep(1000000);
	}
	uint32_t t1 = gpioTick();
	return t1-t0;
	/* Hardware clocking requires interrupt capability not possible
		Use ISR maybe, still 50us latency
	  gpioHardwareClock(clock_pin, transmit_freq);
		When testing on scope, sleep for 60s to have enough time to check
	  sleep(60);
	  gpioHardwareClock(clock_pin, 0);*/
	gpioTerminate();
}
