import RPi.GPIO as GPIO
import time

# Sampling frequency in Hz
sample_freq = 100
timeVal = []
timeDif = []
total = 0
try:
    GPIO.setmode(GPIO.BCM)
    # Setup pin for input PUD_DOWN pull-down resistor
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    print("Interrupt successful, starting to receive")
    output = [1,0,1,1,1,1,0,1,0,1,1,1]
    still_receiving = True
    # Sample at freq until the line stops transmitting
    #-----EVERY BIT-----
    n = 0
    while n<50:
        timeVal.append(time.time())
        output.append(GPIO.input(4))
        time.sleep(1/sample_freq)
        # Stop receiving if the last 8 inputs were zero (data stream closed)
        #if len(output)>8 and output[-8:] == [0]*8 and n>50:
        #    still_receiving = False
        n = n+1
    
    ''' -----LARGE PERIOD----- 
    while still_receiving:
        for i in range(1,50):
            timeVal.append(time.time())
            output.append(GPIO.input(4))
            time.sleep(1/sample_freq)
        # Stop receiving if the last 8 inputs were zero (data stream closed)
        timeVal.append(time.time())
        if len(output)>8 and output[-8:] == [0]*8:
            still_receiving = False
        timeVal.append(time.time())'''

    for i in range(0,len(timeVal)-1):
        timeDif.append(timeVal[i+1]-timeVal[i])
    for i in timeDif:
        print(i)
        total = total + i
    print("AVE TIME  = {}".format(total/len(timeDif)))
    
except KeyboardInterrupt:
    print("Exiting on keyboard interrupt!")
except:
    print("Exiting on unexpected error")

finally:
    GPIO.cleanup()
