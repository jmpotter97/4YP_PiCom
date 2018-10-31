#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc
#include <pigpio.h> // for gpio access
#include <unistd.h> // for sleep(seconds), uint32_t
#include <string.h> // for strlen(string)

const int CLK_PIN = 16;
const int ADC_CLK = 4;
int mask_size;
uint32_t pin_state = 0;
uint32_t* receive_data_mask;
const uint ADC_1_bits[8] = {10, 9, 11, 5, 6, 13, 19, 26}; // MSB to LSB
const uint ADC_2_bits[8] = {14, 15, 18, 17, 27, 22, 23, 24};


// Callback function is automatically passed gpio (will be clock_pin),
// level (0_falling, 1_rising, 2_watchdog) and tick (to compare times)
// gpioTick() (uint32_t) gets tick at any time in code, microseconds since boot
void readPins(int gpio, int level, uint tick) {
	//extern uint32_t pin_state;
    //uint32_t current_state = pin_state;
    extern uint32_t* receive_data_mask;
    static int count = 0;

    if(level==1) {
        if (count < mask_size) {
            receive_data_mask[count++] = gpioRead_Bits_0_31();
            //*((uint32_t*)(data + count++)) = gpioRead_Bits_0_31();
            // Omits superfluous pointer allocation:
            // uint32_t* new_data = (uint32_t*)(data+count++);
            // new_data* = current_state;

            // For testing:
            //printf("%i\n", count);
            if(count == 0)
                // Once transmission started, reduce timeout to 1 second after last clock pulse
				gpioSetWatchdog(CLK_PIN, 1000);
        } else {
            gpioSetAlertFunc(CLK_PIN, 0);
            gpioSetWatchdog(CLK_PIN,0);
            /*for(int i=0;i<8;i++) {
				gpioSetAlertFunc(ADC_1_bits[i], 0);
				gpioSetAlertFunc(ADC_2_bits[i], 0);
		    }*/
		    extern uint32_t pin_state;
            pin_state = 4294967295;
            // 4294967295 is (2^32 - 1) all pins = 1
            printf("Mask size completely received!\nNumber of masks received: %i\n",mask_size);
        }
    } else if(level == 2) {
        gpioSetAlertFunc(CLK_PIN, 0);
        gpioSetWatchdog(CLK_PIN,0);
        /*for(int i=0;i<8;i++) {
			gpioSetAlertFunc(ADC_1_bits[i], 0);
			gpioSetAlertFunc(ADC_2_bits[i], 0);
		}*/
		extern uint32_t pin_state;
        pin_state = 4294967295;
        printf("Watchdog timeout on clock pin!\nNumber of masks received: %i",count);
    }
}

/* Updates global variable pin_state so it can be read immediately on clock pulse
void checkPins(int gpio, int level, uint tick) {
    extern uint32_t pin_state;
    pin_state = gpioRead_Bits_0_31();
}*/

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
    printf("Expected number of masks: %i",mask_size);
    
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
    extern uint32_t* receive_data_mask;
    receive_data_mask = (uint32_t*)calloc(mask_size, sizeof(uint32_t));
    if(receive_data_mask == NULL){
        printf("Memory was not allocated!\n");
        gpioTerminate();
        return 4;
    } else printf("Receive Memory Allocated\n");

    extern uint32_t pin_state;
    pin_state = gpioRead_Bits_0_31();

    /*for(int i=0;i<8;i++) {
        gpioSetAlertFunc(ADC_1_bits[i], checkPins);
        gpioSetAlertFunc(ADC_2_bits[i], checkPins);
    }*/
    
    // Replaced hardware clock with ADC clock capacitor as simpler
    //gpioHardwareClock(ADC_CLK, 10000);
    
    //gpioSetAlertFuncEx(CLK_PIN, readPins, (void*)receive_data_mask);
    gpioSetAlertFunc(CLK_PIN, readPins);
    // Timeout if clock stays silent for 10 seconds
    gpioSetWatchdog(CLK_PIN, 10000);
    
    // Loop until the callback is turned off i.e. transmission finished
    while(1) {
        // All pins set to 1 (which will never happen unless program
        // ends and sets this variable to all 1's)
        if(pin_state == 4294967295)
            break;
        sleep(1);
        //gpioWrite(ADC_CLK,0);
        //usleep(10);
        //gpioWrite(ADC_CLK,1);
        //usleep(9999);
    }

    // Replaced hardware clock with ADC clock capacitor as simpler
    //gpioHardwareClock(ADC_CLK, 0);
    

    /*********************   WRITE TO FILE   *********************/
    printf("WRITE TO FILE\n");
    FILE* out_f;
    char* path = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/data_masks.bin";

    out_f = fopen(path,"wb");
    // Removing of other pins is done in python file (& ADC_Mask)
    /*for(int i = 0;i<mask_size;i++){
		printf("%i\n",receive_data_mask[i]);
	}*/
    fwrite(receive_data_mask, sizeof(uint32_t), mask_size, out_f);
    fclose(out_f);
	
	free(receive_data_mask);
	gpioTerminate();
	return 0;
}
