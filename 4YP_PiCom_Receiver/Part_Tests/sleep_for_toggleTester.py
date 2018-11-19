import RPi.GPIO as GPIO
import time
import datetime

# Toggle frequency in Hz
freq = 100
timeVal = []
timeDif = []
total = 0

'''print("Testing saving time values successively then printing at the end")
print("Difference (seconds) between saves")
for i in range(0,1000): # compared to actually timeVal.append written 1000 times
    timeVal.append(time.time())'''

try:
    GPIO.setmode(GPIO.BCM)
    # Setup pin for output
    GPIO.setup(4, GPIO.OUT)

    for i in range (0,1000):
        #t1=time.time()
        timeVal.append(time.time())
        GPIO.output(4, GPIO.HIGH)
        time.sleep(1/freq-104e-6)#-(time.time()-t1))
        #t2=time.time()
        timeVal.append(time.time())
        GPIO.output(4, GPIO.LOW)
        time.sleep(1/freq-104e-6)#-(time.time()-t2))
    
    for i in range(0,len(timeVal)-1):
        timeDif.append(timeVal[i+1]-timeVal[i])
    for i in timeDif:
        print(i-1/freq)
        total = total + i
    print("AVE TIME MISSING  = {}".format(total/len(timeDif)-1/freq))
    
   
except KeyboardInterrupt:
    print("Exiting on keyboard interrupt!")
except:
    print("Exiting on unexpected error")

finally:
    GPIO.cleanup()
