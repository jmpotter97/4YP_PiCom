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

const uint CLK_PIN = 4;

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}

	/*  argv should have values:
		argv[1] = transmit_freq - Frequency of clock signal, or take default:

	//int transmit_freq = 5000; -- DEPRECATED FOR NOW
	if(argc>2) {
		transmit_freq = atoi(argv[2]); -- DEPRECATED FOR NOW
	} else {
		printf("PiTransmit_2\n\n");
		printf("Usage: ./PiTransmit_3 transmit_freq \n");
		return 3;
	}*/
	
	
	const uint DAC_1_bits[8] = {5,6,13,19,26,21,20,16};
	//TODO: const uint DAC_2_bits[8]; WHEN I CHOOSE PINS FOR DAC2
	for(int i=0;i<8;i++) {
		// It will work without this (knowing DAC pins) but good practice
		gpioSetMode(DAC_1_bits[i], PI_OUTPUT);
		gpioSetMode(DAC_2_bits[i], PI_OUTPUT);
	}
	gpioSetMode(CLK_PIN, PI_OUTPUT);
	
	/////////////////////////////////////////////////////////////////////
	
	FILE* mask_file, mask_inv_file;
    long size, size_inv;
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
	
	if(size == size_inv) {
		uint32_t* transmit_data_mask = calloc(size/size_32int, size_32int);
		fread(transmit_data_mask, size_32int, size/size_32int, mask_file);
		fclose(mask_file);
		uint32_t* transmit_data_mask_inv = calloc(size/size_32int, size_32int);
		fread(transmit_data_mask_inv, size_32int, size/size_32int, mask_file_inv);
		fclose(mask_file_inv);
	} else {
		// MASK AND MASK_INV FILES DIFFERENT LENGTHS
		fclose(mask_file);
		fclose(mask_file_inv);
		return 4;
	}

    for(int i = 0; i<256; i++) {
        printf("%i\n", transmit_data[i]);
    }
    
    /////////////////////////////////////////////////////////////////
	
	for(int i=0; i<size; i++) {
		gpioWrite_Bits_0_31_Clear(transmit_data_mask_inv[i]);
		gpioWrite_Bits_0_31_Set(transmit_data_mask[i]);
		// Low-going CS signal loads data (min low CS 10ns, min high CS 7ns)
		gpioWrite(CLK_PIN, 0);
		usleep(100);
		gpioWrite(CLK_PIN,1);
		usleep(100);
	}
	
	/* SEE  PITRANSMIT_2 FOR NOTES ON CALLBACK FUNCTION IN TRANSMITTER*/
	gpioTerminate();
	return 0;
}
