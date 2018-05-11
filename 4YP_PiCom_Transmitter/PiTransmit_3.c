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
	gpioTerminate();
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}

	/*  argv should have values:
		argv[1] = symbol_freq - Frequency of clock signal,
									or take default (Hz)
	*/
	int symbol_freq = 500000;
	if(argc>1) {
		symbol_freq = atoi(argv[1]);
		// Returns 0 if not a number string (and 0 not OK freq anyway)
		if(symbol_freq == 0) {
			printf("--- PiTransmit_3 ---\n\nInvalid Frequency - zero or not a number\n");
			printf("Usage: ./PiTransmit_3 symbol_freq \n");
			gpioTerminate();
			return 3;	 
		} else if(symbol_freq > 100000) {
            printf("--- PiTransmit_3 ---\n\nInvalid Frequency - over 100kHz is too fast for the current ADC\n");
            printf("Usage: ./PiTransmit_3 symbol_freq \n");
            gpioTerminate();
            return 3;
        }
	}
	// Clock full period in micro-seconds minus 2us (explained in TRANSMIT DATA)
	const int symbol_time = (1000000 / symbol_freq) - 2;
	printf("Frequency (baud rate): %i Hz\n", symbol_freq);
	
	
	const uint DAC_1_bits[8] = {10, 9, 11, 5, 6, 13, 19, 26}; // MSB to LSB
	const uint DAC_2_bits[8] = {14, 15, 18, 17, 27, 22, 23, 24};
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

    // Add CLK_PIN to the inverted mask so the clock is set to zero simultaneous with the
    // data values being set (and then only rising clock edge to latch data required_
    for(int i=0; i<num_of_masks; i++) {
        transmit_data_mask_inv[i] |= (1<<CLK_PIN);
	}

	printf("TRANSMIT DATA\n");
	uint32_t t0 = gpioTick();
	for(int i=0; i<num_of_masks; i++) {
		gpioWrite_Bits_0_31_Clear(transmit_data_mask_inv[i]);
		gpioWrite_Bits_0_31_Set(transmit_data_mask[i]);

        /* Clock cycle will have shape
         * |_|------------|_|------------|_|------------|_|------------
         * The pulses will be low for 2us ^ and high ^ for the rest of the clock period
         * ADC:
         * Rising _CS_ latches data but read event requires falling then rising edge
         * It holds the output at the latched value until the next falling edge
         * DAC:
         * _WR_ going low clears the converter and _WR_ high starts the conversion
         * _BUSY_ goes high when conversion is complete, and is used as Rx clock pin
         *
         * A 2us pulse is definitely long enough for both converters to use as a trigger (100ns at least)
         * It's also short enough that at max frequency (100kHz) this is still a fraction of total time*/

        // gpioWrite(CLK_PIN, 0); is now integrated with the Clear mask
        usleep(2);
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
	free(transmit_data_mask);
	free(transmit_data_mask_inv);
	gpioTerminate();
	return 0;
}
