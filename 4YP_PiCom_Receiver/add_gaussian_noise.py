'''
J. Potter

A function to introduce gaussian noise to the output of the ADC for OOK

OOK has been integrated from the previous versions, uses different pins and runs
using RPi.GPIO and python arrays instead of a C executable (pigpio) and NumPy arrays


Want this function to come into effect before data received at pin is interpreted as 'high' or 'low'
in out.append(GPIO.input(DATA_PIN)) line
becomes out.append(GPIO.input(DATA_PIN) + numpy.random.normal(mu, sigma, None))

Do we add one value as is one sample, or should I create an oscillating wave function of certain freq to go on top of values?

Add this function into receiver code after Receive_Binary_Data
'''

import numpy as np

mu,sigma = 0.0, 0.1

def add_white_noise(mu,sigma,output):
    for value in output:
        value = value + numpy.random.normal(mu, sigma, None)
    return output