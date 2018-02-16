# Using GPIO library for Raspberry Pi
import RPi.GPIO as GPIO
from time import sleep

transmit_freq = 100

def transmit_binary_data(dataList):
    if not all(b == 0 or b == 1 for b in dataList):
        print("Data to transmit is not binary, stopping transmission")
    else:
        # Adding padding to data
        dataList[:0] = [0]+[1]*8+[0]
        dataList[-1:] = [0]+[1]*8+[0]
        print("SIZE OF INPUT = {}".format(len(dataList)))
        print("Transmitting data")
        for b in dataList:
            GPIO.output(4, b)
            sleep(1/transmit_freq)
        GPIO.output(4, GPIO.LOW)
        print("Data transmission complete!")

try:
    # Use BCM numbering standard
    GPIO.setmode(GPIO.BCM);
    # Set BCM pin 4 as an output
    GPIO.setup(4, GPIO.OUT, initial=GPIO.LOW)

    while True:
        GPIO.output(4,GPIO.HIGH)
        #sleep(1/(2*transmit_freq))
        GPIO.output(4,GPIO.LOW)
        #sleep(1/(2*transmit_freq))
    #data = [0]*100
    #sleep(2)
    #transmit_binary_data(data)
    
    print("Finishing program")
        
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
    
finally:
    GPIO.cleanup()
