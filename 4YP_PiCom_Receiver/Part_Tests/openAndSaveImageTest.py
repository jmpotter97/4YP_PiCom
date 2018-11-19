import numpy as np
import imageio as io
import matplotlib.pyplot as plt
import random

def pause(string = ""):
        if string != "":
                string += "\n"
        prPause = input(string+"Pause, press <ENTER> to continue...")


pause("Start")
cat = io.imread('cat.png', pilmode = "RGB")
'''
print(cat.shape)
cat = cat.reshape(cat.size)
print(cat.shape)
cat = cat.reshape(400,400,3)
print(cat.shape)
'''
size = cat.size
output_cat = cat.reshape(size)
print("Length is {}".format(size))

skip=6
for i,data in enumerate(output_cat[size//6:5*size//3:skip]):
    output_cat[i*skip+size//6] = random.randint(0,255)

print(output_cat.shape)
pause("And after the nonsense")

io.imwrite('output_cat.png', output_cat.reshape(400,400,3))
        
print("Done!!!")
