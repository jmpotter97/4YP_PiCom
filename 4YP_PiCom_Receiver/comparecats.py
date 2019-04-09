'''
A function to compare the outputs of the receiver in terms of bit error rate.
'''

import imageio as io
import numpy as np

orig = np.unpackbits(io.imread('cat2_bw.jpg'))
#2k low range
c1 = np.unpackbits(io.imread('cat2_out 4PAM 2018-05-11 15:27.jpg'))
#2k best range
c2 = np.unpackbits(io.imread('cat2_out 4PAM 2018-05-11 16:26.jpg'))
#2k abuse range
c3 = np.unpackbits(io.imread('cat2_out 4PAM 2018-05-11 17:17.jpg'))
#1 best range
c4 = np.unpackbits(io.imread('cat2_out 4PAM 2018-05-11 17:54.jpg'))

err1, err2, err3, err4 = 0, 0, 0, 0

for i in range(orig.size):
    if not orig[i]-c1[i]:
        err1+= 1
    if not orig[i]-c2[i]:
        err2+= 1
    if not orig[i]-c3[i]:
        err3+= 1
    if not orig[i]-c4[i]:
        err4+= 1

print("Bit Error 1 = {}\nBit Error 2 = {}\nBit Error 3 = {}\nBit Error 4 = {}"\
      .format(err1,err2,err3,err4))
print("Average Orig = {}\nAverage 1 = {}\nAverage 2 = {}\nAverage 3 = {}\nAverage 4 = {}"\
      .format(np.average(orig),np.average(c1),np.average(c2),np.average(c3),np.average(c4)))

