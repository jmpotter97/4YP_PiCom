import numpy as np
import matplotlib.pyplot as plt
import random


def pause():
	prPause = input("Pause, press <ENTER> to continue...")


with open('cat.png', 'rb') as f:
    cat = f.read()
    
output_cat = []
for byte in cat:
    output_cat.append(byte)
print("Length is {}".format(len(output_cat)))
length = len(output_cat)

print(output_cat[length//3-1:length//3+2])

skip=1800
for i,data in enumerate(output_cat[length//3:2*length//3:skip]):
    output_cat[i*skip+length//3] = random.randint(0,255)

print("And after the nonsense")
print(output_cat[length//3-1:length//3+2])
#pause()
#output_cat[69998]=0

with open('output_cat.png', 'wb') as f:
    f.write(bytes(output_cat))
        
print("Done!!!")
