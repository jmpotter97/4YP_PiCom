import RPi.GPIO as GPIO
import time

# Sampling frequency in Hz
sample_freq = 100
timeVal = []
timeDif = []
total = 0
LOGS = ""
'''
LOGS = LOGS+"...\n"
with file.open() as f
f.write()
LOGS.split("\n")
'''


def remove_padding(dataList):
    # Remove external padding from data
    stripExtra(0, dataList, False) # Remove trailing zeros
    stripExtra(1, dataList, True)  # Remove front padding ones
    stripExtra(1, dataList, False) # Remove rear padding ones
    # Remove internal continuous value padding
    i = 5
    while i <= len(dataList):
        if dataList[i-5:i] == [0]*5:
            dataList.remove(i)
            i = i + 4
        elif dataList[i-5:i] == [1]*5:
            dataList.remove(i)
            i = i + 4
        i = i + 1
    print("SIZE OF OUTPUT = {}".format(len(dataList)))

def stripExtra(value_to_strip, list_to_strip, front_T_or_F):
    if front_T_or_F == True:
        while list_to_strip[0] == value_to_strip:
            del list_to_strip[0]
    elif front_T_or_F == False:
        while list_to_strip[-1] == value_to_strip:
            list_to_strip.pop()

try:
    GPIO.setmode(GPIO.BCM)
    # Setup pin for input pull-down (PUD_DOWN) resistor
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Receive variables
    output = []
    still_receiving = True

    # Wait for interrupt ########POTENTIALLY PRINT AND WAIT IF POSSIBLE#####
    channel = GPIO.wait_for_edge(4, GPIO.RISING, timeout=10000)     
    # Sample at freq until the line stops transmitting
    timeVal.append(time.time())
    if channel is not None:
        while still_receiving:
            output.append(GPIO.input(4))
            # Stop receiving if the last 8 inputs were zero (data stream closed)
            if len(output)>8 and output[-8:] == [0]*8:
                still_receiving = False
            # Sleep for cycle minus the time it took in the loop
            timeVal.append(time.time())
            time.sleep(1/sample_freq - (timeVal[-1]-timeVal[-2]))
            
        print("Interrupt successful, receiver was started")

        ### cleanOutput = remove_padding(output) ###
        
        print("Writing received data to file")
        with open('/home/pi/Documents/output.txt','w') as f:
            f.write("".join(str(i) for i in output[0:-8]))##################
        # Evaluate time over while loop iterations 
        for i in range(0,len(timeVal)-1):
            timeDif.append(timeVal[i+1]-timeVal[i])
        for i in timeDif:
            total = total + i
        print("AVERAGE RECEIVER WHILE LOOP TIME  = {}".format(total/len(timeDif)))
    else:
        print("Receiver timeout waiting for signal")
            
except KeyboardInterrupt:
    print("Exiting on keyboard interrupt!")
except:
    print("Exiting on unexpected error")

finally:
    GPIO.cleanup()
