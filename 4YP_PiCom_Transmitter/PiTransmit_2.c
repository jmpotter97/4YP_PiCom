#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)

int z = 0;
const uint clock_pin = 4;

// DAC_bits is a bit mask of the GPIO pins which that DAC uses, expressed here
// in the form b7,...,b0. This is XOR'd with the gpioWrite_Bits_0_31_Set bit mask
// (which is passed to this program to get the bit mask for gpioWrite_Bits_0_31_Clear 
const uint DAC_1_bits[8] = {5,6,13,19,26,21,20,16};
//const uint DAC_2_bits[8];
int DAC_1_mask = (1<<5)|(1<<6)|(1<<13)|(1<<19)|(1<<26)|(1<<21)|(1<<20)|(1<<16);//, DAC_2_mask;

/*for(int i=0;i<8;i++) {
	DAC_1_mask = DAC_1_mask|(1<<DAC_1_bits[i]);
	DAC_2_mask = DAC_2_mask|(1<<DAC_2_bits[i]);
}*/
//int DAC_mask = 0 | DAC_1_mask | DAC_2_mask;

void newState() {
	if(z++%50<25){
		gpioWrite_Bits_0_31_Clear(DAC_1_mask);
		gpioWrite_Bits_0_31_Set(0);
	} else {
		gpioWrite_Bits_0_31_Clear(0);
		gpioWrite_Bits_0_31_Set(DAC_1_mask);
	}
}

int main(int argc, char *argv[]) {
	// REMEMBER TO CHANGE SAMPLE RATE OF GPIO's, STANDARD IS 5us
	// gpioCfgClock()
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
	printf("Hello World\n");

	// argv should have values:
	// argv[1] = size_of_input
	// argv[2] = transmit_data - This is a bit mask, fed as a char
	// 			 array, for gpioWrite_Bits_0_31_Set
	// argv[3] = 
	int transmit_freq = 5000;
	// Receive actual transmit frequency from main arguments
	/*if(argc>1) transmit_freq = atoi(argv[1]);
	else { printf("GPIO INIT FAIL\n"); return 1;}
	if(argc>2) transmit_freq = atoi(argv[2]);


	

	data_mask = calloc(sizeof(transmit_data-1)/4,sizeof(uint32_t));
	for(int i = 1; i<(sizeof(transmit_data)-1)/4; i++) {
		int mask_convert[4];
		for(int j=0;j<4,j++) {
			sscanf(transmit_data[i+j-4],"%x",&mask_convert[j]);
			// data_mask[i] = mask_convert[0]<<12 + mask_convert[1]<<8 + mask_convert[2]<<4 + mask_convert[3];
			data_mask[i] += mask_convert[j]<<((3-j)*3);
		}
	}*/
	
	for(int i=0;i<8;i++) {
		gpioSetMode(DAC_1_bits[i], PI_OUTPUT);
	}
	gpioHardwareClock(clock_pin, transmit_freq);
	gpioSetAlertFunc(clock_pin,newState);
	sleep(60);
	gpioHardwareClock(clock_pin, 0);
	gpioTerminate();
}
