'''
J. Potter based on code by C. Eadie

A function to evaluate the frequency/BER characteristics of the OOK set-up

OOK has been integrated from the previous versions, uses different pins and runs
using RPi.GPIO and python arrays instead of a C executable (pigpio) and NumPy arrays
'''

import numpy as np
import paramiko
from time import sleep

'''---------------------------   On-Off Keying   ---------------------------'''
def Add_Padding(unpadded_data):
    data = []
    for i in range(50):
        data.append(0)
    for i in unpadded_data:
        data.append(i)
    for i in range(50):
        data.append(0)
    return data

def Get_OOK_Data(length):
    unpadded_data = []
    for i in range(int(length/2)):
        #i = int(np.random.randint(2, size=1))
        #unpadded_data.append(i)
        unpadded_data.append(int(1))
        unpadded_data.append(int(0))
    return unpadded_data

def Transmit_Binary_Data(data_list,OOK_TRANS_FREQ):
    import RPi.GPIO as GPIO
    overclocking = 1
    try:
        # Use BCM numbering standard
        GPIO.setmode(GPIO.BCM);
        CLK_PIN = 20
        DATA_PIN = 21
        # Set BCM pin 4 as an output
        GPIO.setup(DATA_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#initial=GPIO.LOW)
        half_clock_clock = 1 / ((2 * OOK_TRANS_FREQ)*overclocking) #overclock - number of clock cycles per bit       
        half_clock_data = 1 / (2 * OOK_TRANS_FREQ)
        print("Transmitting data")
        for b in data_list:
            GPIO.wait_for_edge(CLK_PIN, GPIO.FALLING, timeout=1000)
            GPIO.output(DATA_PIN, b)
            #for i in range(overclocking):
             #   GPIO.output(CLK_PIN, GPIO.HIGH)            
              #  sleep(half_clock_clock)
               # GPIO.output(CLK_PIN, GPIO.LOW)
                #sleep(half_clock_clock)
        GPIO.output(DATA_PIN, GPIO.LOW)
        print("Data transmission complete!")        
    except KeyboardInterrupt:
        print("\nExiting program on keyboard interrupt")
    except Exception as e:
        print("\nExiting program on unexpected error\nError is: {}".format(e))
    finally:
        print("Cleaning up GPIOs")
        GPIO.cleanup()

'''--------------------------------   SSH   --------------------------------'''

def Ssh_Start_Receiver(mask_length):
    print("Starting Receiver")    
