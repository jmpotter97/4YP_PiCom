import RPi.GPIO as GPIO
#from RPiSim.GPIO import GPIO
from time import time


GPIO_STATE = [0, 0, 0, 0, 0, 0, 0, 0]
GPIO_PINS = [5, 6, 13, 19, 26, 21, 20, 16]
CLK_PIN = 4

def getDummyData():
    print("Full transition")
    arr = ([1,0] * 4 + [0,1]*4 )*1000
    return arr

def chunks(l, n):

    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def convertToTransform(input):

    #Split into bytes
    bytes = list(chunks(input, 8))

    #Create l -> l' transform
    transform = []
    transform.append(bytes[0]) #First byte transform is the initial setting
    previousState = transform[0]

    for byteOut in bytes[1:]:
        newTransform = []
        for b, bPrime in zip(previousState, byteOut):
            newTransform.append(b ^ bPrime)
        transform.append(newTransform)



    return transform

def setGPIOHeaders(b):

    #Flip GPIO pins on values of b == 1
    for gpioItt, bitOut in enumerate(b):
        if bitOut:
            if GPIO_STATE[gpioItt]:
                #Pin is high, set low
                GPIO_STATE[gpioItt] = 0
                GPIO.output(GPIO_PINS[gpioItt],GPIO.LOW)

            else:
                #Pin is low, set high
                GPIO_STATE[gpioItt] = 1
                GPIO.output(GPIO_PINS[gpioItt],GPIO.HIGH)

    #Set the clock
    GPIO.output(CLK_PIN, GPIO.HIGH)
    #Check for rising edge
    GPIO.output(CLK_PIN, GPIO.LOW)
    #Check for falling edge


if __name__ == '__main__':
    a = getDummyData()

    GPIO.setmode(GPIO.BCM)
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(CLK_PIN, GPIO.OUT, initial=GPIO.LOW)

    transforms = convertToTransform(a)
    #print(transforms)

    t0 = time()
    for transform in transforms:
        setGPIOHeaders(transform)
    t1 = time()-t0
    print("Bit rate")
    print(str(t1/16000))
    print("Byte rate")
    print(str(t1/2000))
    print("Bit frequency")
    print(str(1/(t1/16000)))

    GPIO.cleanup()
    print('fin')
