'''
J. Potter

A function to measure the accuracy of the 'sleep' function in python.
'''

from time import sleep
from time import time

wait_times = [1,0.1,0.01,0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001]
runs = 10

for wait in wait_times:
    waits = []
    for run in range(runs):
        start = time()
        sleep(wait)
        end = time()
        actual_wait = end - start
        waits.append(actual_wait)
    total_waits = 0
    for w in waits:
        total_waits += w
    average_actual_wait = total_waits/len(waits)
    frequency = 1/average_actual_wait
    print("Expected delay: {}, Actual delay: {}, Corresponding Frequency: {}".format(wait, average_actual_wait, frequency))
