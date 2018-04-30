#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds), uint32_t
#include <string.h> // for strlen(string)

const int CLK_PIN = 16;
const int ADC_CLK = 4;
int mask_size;
uint32_t pin_state;


// Callback function is automatically passed gpio (will be clock_pin),
// level (0_falling, 1_rising, 2_watchdog) and tick (to compare times)
// gpioTick() (uint32_t) gets tick at any time in code, microseconds since boot
void readPins(int gpio, int level, uint tick, void* data) {
	extern uint32_t pin_state;
    uint32_t current_state = pin_state;
    static int count = 0;

    if(!level) {
        if (count < mask_size) {
            //int* new_data = (int*)(data+count++);
            *((uint32_t*)(data + count++)) = current_state;
            //printf("%i\n", count);
        } else {
            gpioSetAlertFuncEx(clock_pin, 0, NULL);
            gpioSetWatchdog(CLK_PIN,0);
            pin_state = 1<<32 - 1;
            printf("DONE!\n\n");
        }
    } else if(level == 2) {
        gpioSetAlertFuncEx(clock_pin, 0, NULL);
        gpioSetWatchdog(CLK_PIN,0);
        pin_state = 1<<32 - 1;
        printf("Watchdog timeout on clock");
    }
}

// Updates global variable pin_state so it can be read immediately on clock pulse
void checkPins(int gpio, int level, uint tick) {
    extern uint32_t pin_state;
    pin_state = gpioRead_Bits_0_31();
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
        if(mask_size == 0) {
            printf("--- PiTransmit_3 ---\n\nInvalid Mask Size\n");
            printf("Usage: ./PiTransmit_3 mask_size \n");
            gpioTerminate();
            return 5;
        }
    } else {
        printf("--- PiReceive ---\n\n");
        printf("Usage: sudo ./PiReceive mask_size \n");
        gpioTerminate();
        return 3;
    }

    const uint ADC_1_bits[8] = {10, 9, 11, 5, 6, 13, 19, 26}; // MSB to LSB
    const uint ADC_2_bits[8] = {14, 15, 18, 17, 27, 22, 23, 24};
    for(int i=0;i<8;i++) {
        // It will work without this (setting ADC pins) but good practice
        gpioSetMode(ADC_1_bits[i], PI_INPUT);
        gpioSetMode(ADC_2_bits[i], PI_INPUT);
        gpioSetPullUpDown(ADC_1_bits[i], PI_PUD_DOWN);
        gpioSetPullUpDown(ADC_2_bits[i], PI_PUD_DOWN);
    }
    gpioSetMode(CLK_PIN, PI_INPUT);
    gpioSetPullUpDown(CLK_PIN, PI_PUD_DOWN);
    gpioSetMode(ADC_CLK, PI_INPUT);
    gpioSetPullUpDown(ADC_CLK, PI_PUD_DOWN);

    /*********************   RECEIVE DATA   *********************/
    printf("RECEIVE DATA\n");
    uint32_t* receive_data_mask = (uint32_t*)calloc(mask_size, sizeof(uint32_t));
    if(receive_data_mask == NULL){
        printf("Memory was not allocated!\n");
        gpioTerminate();
        return 4;
    } else printf("Receive Memory Allocated\n");
    // TODO: REMEMBER TO FREE

    extern uint32_t pin_state;
    pin_state = gpioRead_Bits_0_31();

    for(int i=0;i<8;i++) {
        gpioSetAlertFunc(ADC_1_bits[i], checkPins);
        gpioSetAlertFunc(ADC_2_bits[i], checkPins);
    }
    gpioHardwareClock(ADC_CLK, 1000000);
    gpioSetAlertFuncEx(CLK_PIN, readPins, (void*)receive_data_mask);
    gpioSetWatchdog(CLK_PIN, 1000);

    // Loop until the callback is turned off i.e. transmission finished
    while(1) {
        // All pins set to 1 (which will never happen unless program
        // ends and sets this variable to all 1's)
        if(pin_state == 1<<32 - 1)
            break;
        sleep(1);
    }

    for(int i=0;i<8;i++) {
        gpioSetAlertFunc(ADC_1_bits[i], 0);
        gpioSetAlertFunc(ADC_2_bits[i], 0);
    }
    gpioHardwareClock(ADC_CLK, 0);

    /*********************   WRITE TO FILE   *********************/
    printf("WRITE TO FILE\n");
    FILE* out_f;
    char* path = "data_masks.bin";

    out_f = fopen(path,"wb");
    // Removing of other pins is done in python file (& ADC_Mask)
    fwrite((void*)receive_data_mask, sizeof(uint32_t), mask_size, out_f);
    fclose(out_f);

	free(receive_data_mask);
	gpioTerminate();
	return 0;
}
