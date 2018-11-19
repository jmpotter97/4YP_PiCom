import RPi.GPIO as GPIO

clock_pin = 18
data_pin = 4
output = []

LOGS = "********** RECEIVER LOG FILE **********\n\n"

def Receive_Data(output):
    # Data signal should start 1 second after clock to allow for callback setup
    # Wait 5 seconds for the data channel to start transmitting, or timeout
    still_receiving = True
    if GPIO.wait_for_edge(data_pin, GPIO.RISING, timeout=5000) is not None:
        output.append(GPIO.input(data_pin))
        while still_receiving:
            # Run until clock edge doesn't change (stops) for 1 second
            if GPIO.wait_for_edge(clock_pin, GPIO.BOTH, timeout=1000) is not None:
                output.append(GPIO.input(data_pin))
            else:
                still_receiving = False
    else:
        LOGS = LOGS + "Data interrput not received, stopping receiver\n"

def Remove_Padding(data_list):
    # Remove trailing (timeout) zeros
    Strip_Extra(data_list, 0, False)
    LOGS = LOGS + "SIZE OF INPUT = {}\n".format(len(data_list))
    
    # Remove external padding from data
    #   11111110 ... 01111111
    Strip_Extra(data_list, 1, True)  # Remove rear padding 1's
    Strip_Extra(data_list, 1, False) # Remove trailing padding '1s
    # Remove extra front and rear 0
    if data_list[0] == 0 and data_list[-1] == 0:
        LOGS = LOGS + "Input fits padding form at least\n"
        del data_list[0]
        data_list.pop()
    else:
        LOGS = LOGS + "Input may have some issues\n"
    
    # Remove internal continuous value padding
    i = 5
    ##### NEEDS LOOKING AT BEFORE INCLUSION #####
    while i <= len(data_list):
        if data_list[i-5:i] == [0]*5:
            data_list.remove(i)
            i = i + 4
        elif data_list[i-5:i] == [1]*5:
            data_list.remove(i)
            i = i + 4
        i = i + 1
    LOGS = LOGS + "SIZE OF OUTPUT = {}\n".format(len(data_list))

def Strip_Extra(list_to_strip, value_to_strip, from_front_T_or_rear_F):
    if front_T_or_F == True:
        while list_to_strip[0] == value_to_strip:
            del list_to_strip[0]
    elif front_T_or_F == False:
        while list_to_strip[-1] == value_to_strip:
            list_to_strip.pop()

def Decode_Error_Correction(output):
    ''' TO BE ADDED '''

def Save_As_Image(output):
    ''' TO BE ADDED '''

try:
    GPIO.setmode(GPIO.BCM)
    # Setup input and clock pins as IN-puts with pull-down (PUD_DOWN) resistor
    GPIO.setup(data_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(clock_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Waiting for clock start interrupt
    #   wait_for_edge will return 'None' on timeout, otherwise it returns
    #   the pin number of clock_pin when the edge is detected
    if GPIO.wait_for_edge(clock_pin, GPIO.RISING, timeout=10000) is not None:
        LOGS = LOGS + "Clock interrupt successful, receiver was started\n"
        Receive_Data(output)
        if len(output) == 0:
            LOGS = LOGS + "No data was received\n"
        else:
            '''
            Remove_Padding(output) ### WILL INCLUDE ONCE CONFIRMED TO WORK, MAYBE
            Decode_Error_Correction(output) ### REPLACES PADDING REALLY
            '''
            LOGS = LOGS + "Saving output to file\n"
            with open('OUTPUT.txt','w') as f:
                f.write("".join(str(i) for i in output))
            '''
            Save_As_Image(output) ### TO DO WHEN POSSIBLE, REMOVE PREVIOUS SAVE TO FILE
            '''
    else:
        LOGS = LOGS + "Receiver timeout waiting for signal\n"
        
            
except KeyboardInterrupt:
    LOGS = LOGS + "\nExiting on keyboard interrupt!\n"
except Exception as e:
    LOGS = LOGS + "\nExiting on unexpected error!\nError is: {}".format(e)

finally:
    with open('LOGS.txt','w') as f:
        f.write(LOGS)
    GPIO.cleanup()
