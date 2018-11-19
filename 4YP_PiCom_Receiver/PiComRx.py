import RPi.GPIO as GPIO
from time import sleep

# Sampling frequency in Hz
sample_freq = 100
try:
    GPIO.setmode(GPIO.BCM)
    # Setup pin for input PUD_DOWN pull-down resistor
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    channel = GPIO.wait_for_edge(4, GPIO.RISING, timeout=10000)
    
    if channel is None:
        print("Timeout waiting for transmission")
    else:
        print("Interrupt successful, starting to receive")
        output = []
        still_receiving = True
        # Sample at freq until the line stops transmitting
        while still_receiving:
            output.append(GPIO.input(4))
            sleep(1/sample_freq)
            # Stop receiving if the last 8 inputs were zero (data stream closed)
            if len(output)>8 and output[-8:] == [0]*8:
                still_receiving = False
        # Remove 8-bit padding from data
        output=output[8:-8]
        print("SIZE OF OUTPUT = {}".format(len(output)))
        print("Writing received data to file")
        with open('/home/pi/Documents/output.txt','w') as f:
            f.write("".join(str(i) for i in output[0:-8]))
    
except KeyboardInterrupt:
    print("Exiting on keyboard interrupt!")
except:
    print("Exiting on unexpected error")

finally:
    GPIO.cleanup()
