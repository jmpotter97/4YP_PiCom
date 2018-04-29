#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds), uint32_t
#include <string.h> // for strlen(string)

const int num_of_ADC = 1;	// TODO: Remove this!!!
#define CLK_PIN = 16;
#define ADC_CLK 4; //TODO: Incorporate this into the code
int mask_size;
uint32_t pin_state;

// Callback function is automatically passed gpio (will be clock_pin),
// level (0_falling, 1_rising,2_watchdog) and tick (to compare times)
// gpioTick() (uint32_t) gets tick at any time in code, microseconds since boot
void readPins(int gpio, int level, uint tick, void* data) {
	static int count = 0;
    
	if(!level){
		if(count >= mask_size) {
            gpioSetAlertFuncEx(clock_pin, 0, NULL);
            printf("DONE!\n\n");
        } else {
			//int* new_data = (int*)(data+count++);
			*((uint32_t*)(data+count++)) = gpioRead_Bits_0_31();
			printf("%i\n",count);
		}
	}
	
}

int main(int argc, char *argv[]) {
	/************************   SETUP   ************************/
    printf("SETUP\n");
    /* CHANGE SAMPLE RATE OF GPIO's (1,2,4,5,8,10),
     * STANDARD IS 5us (200kHz), FASTEST IS 1us (1MHz)
     * FOR 2us : gpioCfgClock(2,1,0);
     * Not necessary as current ADC max freq = 111kHz*/
    if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 2;}

    /*  argv should have values:
        argv[1] = mask_size - Number of symbols to be received
    */
    extern int mask_size;
    if(argc>1) {
        mask_size = atoi(argv[1]);
    } else {
        printf("--- PiReceive ---\n\n");
        printf("Usage: sudo ./PiReceive mask_size \n");
        gpioTerminate();
        return 3;
    }

    const uint DAC_1_bits[8] = {10, 9, 11, 5, 6, 13, 19, 26}; // MSB to LSB
    const uint DAC_2_bits[8] = {2, 3, 4, 17, 27, 22, 23, 24};
    for(int i=0;i<8;i++) {
        // It will work without this (setting DAC pins) but good practice
        gpioSetMode(DAC_1_bits[i], PI_INPUT);
        gpioSetMode(DAC_2_bits[i], PI_INPUT);
    }
    gpioSetMode(CLK_PIN, PI_INPUT);
    gpioSetPullUpDown(CLK_PIN,PI_PUD_DOWN);


    //const int sub_mask_size = 2 * num_of_ADC;
    uint32_t* receive_data_mask = calloc(mask_size, sizeof(uint32_t));
    printf("Yay\n");
    // TODO: REMEMBER TO FREE
    //int receive_data_mask[10];

	/******************************************************************/
	// Using a self-generated clock FOR TESTING
	gpioHardwareClock(clock_pin, 5000);
	gpioSetAlertFuncEx(clock_pin, readPins, (void*)receive_data_mask);
	// When testing on scope, sleep for 60s to have enough time to check
	sleep(5);
	gpioHardwareClock(clock_pin, 0);
	/******************************************************************/
	
	
	
	FILE* out_f;
	out_f = fopen("OUT.txt","w");
	for(int i = 0; i < mask_size; i++) {
		// Save relevant (& ADC_1_mask) bits of receive
		if(i==0) fprintf(out_f, "%i", receive_data_mask[i] & ADC_1_mask);
		else fprintf(out_f, ",%i", receive_data_mask[i] & ADC_1_mask);
	}
	fclose(out_f);
	printf("Pre\n");
	free(receive_data_mask);
	printf("Post\n");
	gpioTerminate();
	printf("Fin\n");
	return 0;
}
