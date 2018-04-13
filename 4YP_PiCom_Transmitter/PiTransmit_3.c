#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds)
#include <string.h> // for strlen(string)

/* PiTransmit now works independent of the choice of DAC pins.
 * It reads in the bit-mask (bits to set) from a binary file for speed,
 * which is calculated and saved in the Python before transmission,
 * and it also reads in inversion mask (bits to clear) so the calculation
 * isn't done during transmission.
 * This also means the Transmit program doesn't need to know how many
 * DAC's there are so works for all transmission schemes.
 */

const uint CLK_PIN = 16;


int main(int argc, char *argv[]) {
	
	/************************   SETUP   ************************/
	printf("SETUP\n");
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}

	/*  argv should have values:
		argv[1] = symbol_freq - Frequency of clock signal,
									or take default (Hz)
	*/
	int symbol_freq = 500;
	if(argc>1) {
		symbol_freq = atoi(argv[1]);
		// Returns 0 if not a number string (and 0 not OK freq anyway)
		if(symbol_freq == 0) {
			printf("PiTransmit_3\n\n");
			printf("Usage: ./PiTransmit_3 symbol_freq \n");
			gpioTerminate();
			return 3;	 
		}
	}
	// Half clock period time in us
	const int symbol_time = 1000000 / (2*symbol_freq);
	printf("Frequency: %i Hz\nHalf-clock-period: %.3f ms\n",
			symbol_freq,symbol_time/1000.0); 
	
	
	const uint DAC_1_bits[8] = {10, 9, 11, 5, 6, 13, 19, 26}; // MSB to LSB
	const uint DAC_2_bits[8] = {2, 3, 4, 17, 27, 22, 23, 24};
    for(int i=0;i<8;i++) {
		// It will work without this (setting DAC pins) but good practice
		gpioSetMode(DAC_1_bits[i], PI_OUTPUT);
		gpioSetPullUpDown(DAC_1_bits[i],PI_PUD_DOWN);
		gpioSetMode(DAC_2_bits[i], PI_OUTPUT);
		gpioSetPullUpDown(DAC_2_bits[i],PI_PUD_DOWN);
	}
	gpioSetMode(CLK_PIN, PI_OUTPUT);
	gpioSetPullUpDown(CLK_PIN,PI_PUD_DOWN);
	
	/*********************   READ IN FILES   *********************/
	printf("READ IN FILES\n");
	FILE* mask_file;
	FILE* mask_file_inv;
    long size;
    long size_inv;
    size_t size_32int = sizeof(uint32_t);
    char* path = "data_masks.bin";
    char* path_inv = "data_masks_inv.bin";

    mask_file = fopen(path, "rb");
    fseek(mask_file , 0 , SEEK_END);
    size = ftell(mask_file);
    rewind(mask_file);
    
    mask_file_inv = fopen(path_inv, "rb");
    fseek(mask_file_inv , 0 , SEEK_END);
    size_inv = ftell(mask_file_inv);
    rewind(mask_file_inv);
	
	if(size != size_inv) {
		// MASK AND MASK_INV FILES DIFFERENT LENGTHS
		fclose(mask_file);
		fclose(mask_file_inv);
		gpioTerminate();
		return 4;
	}
	int num_of_masks = (int)(size/size_32int);
	uint32_t* transmit_data_mask = calloc(num_of_masks, size_32int);
	fread(transmit_data_mask, size_32int, num_of_masks, mask_file);
	fclose(mask_file);
	
	uint32_t* transmit_data_mask_inv = calloc(num_of_masks, size_32int);
	fread(transmit_data_mask_inv, size_32int, num_of_masks, mask_file_inv);
	fclose(mask_file_inv);
    
    /*********************   TRANSMIT DATA   *********************/
    //For Testing:
    //gpioHardwareClock(4, symbol_freq);
	printf("TRANSMIT DATA\n");
	uint32_t t0 = gpioTick();
	for(int i=0; i<num_of_masks; i++) {
		gpioWrite_Bits_0_31_Clear(transmit_data_mask_inv[i]);
		gpioWrite_Bits_0_31_Set(transmit_data_mask[i]);
		// Low-going CS signal loads data (min low CS 10ns, min high CS 7ns)
		usleep(1);
		gpioWrite(CLK_PIN, 0);
		usleep(symbol_time-1);
		gpioWrite(CLK_PIN,1);
		usleep(symbol_time);
		//printf("%i\nPause, press <ENTER> to continue...\n", i);
		//getchar();
		
	}
	uint32_t t1 = gpioTick();
	printf("Total transmission time: %fs\n", (t1 - t0)/1000000.0);
	//For Testing:
	//gpioHardwareClock(4, 0);
	
	/* SEE  PITRANSMIT_2 FOR NOTES ON CALLBACK FUNCTION IN TRANSMITTER*/
	gpioTerminate();
	return 0;
}
