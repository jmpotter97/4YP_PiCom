import imageio as io
import numpy as np
import sys

orig = np.unpackbits(io.imread('cat2_bw.jpg'))
mod_scheme = "PAM"
if mod_scheme == "PAM":
    c1 = np.unpackbits(io.imread('cat2_out_2_4PAM_1k.jpg'))
    c2 = np.unpackbits(io.imread('cat2_out_3_4PAM_2k.jpg'))
    c3 = np.unpackbits(io.imread('cat2_out_4_4PAM_5k.jpg'))
    c4 = np.unpackbits(io.imread('cat2_out_5_4PAM_10k.jpg'))
    c5 = np.unpackbits(io.imread('cat2_out_6_4PAM_50k.jpg'))
    c6 = np.unpackbits(io.imread('cat2_out_7_4PAM_100k.jpg'))
elif mod_scheme == "QAM":
    c1 = np.unpackbits(io.imread('cat2_out_9_16QAM_1k.jpg'))
    c2 = np.unpackbits(io.imread('cat2_out_10_16QAM_2k.jpg'))
    c3 = np.unpackbits(io.imread('cat2_out_11_16QAM_5k.jpg'))
    c4 = np.unpackbits(io.imread('cat2_out_12_16QAM_10k.jpg'))
    c5 = np.unpackbits(io.imread('cat2_out_13_16QAM_50k.jpg'))
    c6 = np.unpackbits(io.imread('cat2_out_14_16QAM_100k.jpg'))
else:
    print("Unreckognised Modulation Scheme...")
    sys.exit(1)

err = [0, 0, 0, 0, 0, 0]

err = np.array([0, 0, 0, 0, 0, 0])
offset = 5
for i in range(orig.size-offset):
    if not int(orig[i])-int(c1[i+offset]):
        err[0] += 1
    if not int(orig[i])-int(c2[i+offset]):
        err[1] += 1
    if not int(orig[i])-int(c3[i+offset]):
        err[2] += 1
    if not int(orig[i])-int(c4[i+offset]):
        err[3] += 1
    if not int(orig[i])-int(c5[i+offset]):
        err[4] += 1
    if not int(orig[i])-int(c6[i+offset]):
        err[5] += 1
ber = 100 * err / orig.size
'''
print(orig.size)
corr = np.correlate(orig,c1,mode="full")
print(corr.shape)
maxi = np.amax(corr)
print(np.where(corr == maxi))
'''
print("Bit Error Rate for {} (with offset {}):\n... {}\n... {}\n... {}\n... {}\n... {}\n... {}"\
      .format(mod_scheme,offset,ber[0],ber[1],ber[2],ber[3],ber[4],ber[5]))
