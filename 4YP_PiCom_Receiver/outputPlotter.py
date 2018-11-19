#sudo apt-get install libatlas-base-dev
#sudo apt-get install python3-gi-cairo
import numpy as np
import matplotlib.pyplot as plt

with open('OUT.txt', 'r') as f:
    i = f.read().split(',')

plt.plot(i)
plt.show()
