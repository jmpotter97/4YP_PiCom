import RPi.GPIO as GPIO
from time import sleep

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    while 1:
        GPIO.output(4, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(4, GPIO.LOW)
        sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting on keyboard interrupt")

finally:
    GPIO.cleanup()
