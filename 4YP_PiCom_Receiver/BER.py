import imageio as io
import numpy as np

orig = np.unpackbits(io.imread('cat2_bw.jpg'))
#250
#c1 = np.unpackbits(io.imread('cat2_4PAM_250Hz.jpg'))
#1k
c1 = np.unpackbits(io.imread('cat2_4PAM_1kHz.jpg'))
#2k
c2 = np.unpackbits(io.imread('cat2_4PAM_2kHz.jpg'))
#5k
c3 = np.unpackbits(io.imread('cat2_4PAM_5kHz.jpg'))
#10k
c4 = np.unpackbits(io.imread('cat2_4PAM_10kHz.jpg'))
#50k
c5 = np.unpackbits(io.imread('cat2_4PAM_50kHz.jpg'))
#100k
c6 = np.unpackbits(io.imread('cat2_4PAM_100kHz.jpg')

err1, err2, err3, err4, err5, err6 = 0, 0, 0, 0, 0, 0

for i in range(orig.size):
    if not orig[i]-c1[i]:
        err1+= 1
    if not orig[i]-c2[i]:
        err2+= 1
    if not orig[i]-c3[i]:
        err3+= 1
    if not orig[i]-c4[i]:
        err4+= 1
    if not orig[i]-c5[i]:
        err5+= 1
    if not orig[i]-c6[i]:
        err6+= 1


print("Bit Error 1 = {}\nBit Error 2 = {}\nBit Error 3 = {}\nBit Error 4 = {}\nBit Error 5 = {}\nBit Error 6 = {}"\
      .format(err1,err2,err3,err4,err5,err6))
print("Average Orig = {}\nAverage 1 = {}\nAverage 2 = {}\nAverage 3 = {}\nAverage 4 = {}\nAverage 5 = {}\nAverage 6 = {}"\
      .format(np.average(orig),np.average(c1),np.average(c2),np.average(c3),np.average(c4),np.average(c5),np.average(c6)))




