import numpy as np
import matplotlib.pyplot as plt
import imageio as io
import sys
from math  import sqrt

DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [14, 15, 18, 17, 27, 22, 23, 24]

def RMS(amplitudes):
    sq = np.square(np.abs(amplitudes))
    av = np.average(sq)
    return sqrt(av)

def MagSignal(data_list,TRANSMISSION_TYPE):
    if TRANSMISSION_TYPE == "4PAM":
        # 4 SYMB/byte --> 0, 1, 2, 3
        mapping_table = {(0,0) : 0,
                         (0,1) : 1,
                         (1,0) : 2,
                         (1,1) : 3}
        def Mapping(bits):
            return np.array([mapping_table[tuple(b)] for b in bits])

        
        data_list_bits = np.unpackbits(data_list)\
                         .reshape((np.unpackbits(data_list).size//2,2))
        symb = Mapping(data_list_bits)

        symb = symb * 3.3/3
        return symb
        
    elif TRANSMISSION_TYPE == "16QAM":
        # 2 SYMB/byte --> I = 0, 1, 2, 3 : Q = 0, 1, 2, 3 SYMB is I,Q
        # Expressing I as col 1, Q as col 2 of N x 2 matrix
        mapping_table = {
            (0,0,0,0) : 0 + 0j,
            (0,0,0,1) : 0 + 1j,
            (0,0,1,0) : 0 + 3j,
            (0,0,1,1) : 0 + 2j,
            (0,1,0,0) : 1 + 0j,
            (0,1,0,1) : 1 + 1j,
            (0,1,1,0) : 1 + 3j,
            (0,1,1,1) : 1 + 2j,
            (1,0,0,0) : 3 + 0j,
            (1,0,0,1) : 3 + 1j,
            (1,0,1,0) : 3 + 3j,
            (1,0,1,1) : 3 + 2j,
            (1,1,0,0) : 2 + 0j,
            (1,1,0,1) : 2 + 1j,
            (1,1,1,0) : 2 + 3j,
            (1,1,1,1) : 2 + 2j
            }
        def Mapping(bits):
            return np.array([mapping_table[tuple(b)] for b in bits])

        
        data_list_bits = np.unpackbits(data_list)\
                         .reshape((np.unpackbits(data_list).size//4,4))
        symb = Mapping(data_list_bits)
        symb = symb * 3.3/3
        return symb
    else:
        print("Dumb son of a bittch")    


def MagNoiseySig(masks,TRANSMISSION_TYPE):
    if TRANSMISSION_TYPE == "4PAM":
        # Will use maximum likelihood reconstruction and account for attenuation
        # DAC
        # Masks are 32-bit
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            masks[i] = val
        # Masks are 8-bit but attenuated
        highest = max(masks)
        lowest = min(masks)
        # SYMB
        for i in range(masks.size):
            if highest != 255 and highest != lowest and highest != 0:
                masks[i] = round((masks[i]-lowest)*255/(highest-lowest))
        masks = masks * 3.3 / 255
        return masks
        
    elif TRANSMISSION_TYPE == "16QAM":
        # DAC
        # Masks are 32-bit
        dac = np.zeros(masks.size, dtype='complex')
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            dac[i] = val
            val=0
            for j, pin in enumerate(DAC_PINS_2):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            dac[i] += val * 1j
        # DAC values are 8-bit but attenuated
        highest = int(max(np.hstack((dac.real,dac.imag))))
        lowest = int(min(np.hstack((dac.real,dac.imag))))
        # SYMB
        for i in range(dac.size):
            re = dac[i].real
            im = dac[i].imag
            if highest != 255 and highest != lowest and highest != 0:
                dac[i] = round((re-lowest)*255/(highest-lowest))\
                         + round((im-lowest)*255/(highest-lowest))*1j
        dac = dac * 3.3 / 255
        return dac
    else:
        print("Dumb son of a bittch")
           

orig = io.imread('cat2_bw.jpg')
orig = orig.reshape((orig.size,))

TRANSMISSION_TYPE = "4PAM"
# Fewer data points as I forgot to rename the data masks and wrote over some
c0P = MagNoiseySig(np.fromfile('data_masks_1_4PAM_500.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c4P = MagNoiseySig(np.fromfile('data_masks_5_4PAM_10k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c5P = MagNoiseySig(np.fromfile('data_masks_6_4PAM_50k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)

signalP = MagSignal(orig,TRANSMISSION_TYPE)
signalPRMS = RMS(signalP)

TRANSMISSION_TYPE = "16QAM"
c0 = MagNoiseySig(np.fromfile('data_masks_8_16QAM_500.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c1 = MagNoiseySig(np.fromfile('data_masks_9_16QAM_1k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c2 = MagNoiseySig(np.fromfile('data_masks_10_16QAM_2k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c3 = MagNoiseySig(np.fromfile('data_masks_11_16QAM_5k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c4 = MagNoiseySig(np.fromfile('data_masks_12_16QAM_10k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c5 = MagNoiseySig(np.fromfile('data_masks_13_16QAM_50k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)
c6 = MagNoiseySig(np.fromfile('data_masks_14_16QAM_100k.bin', dtype = 'uint32'),TRANSMISSION_TYPE)

signal = MagSignal(orig,TRANSMISSION_TYPE)
signalRMS = RMS(signal)

n0RMSP = RMS(np.subtract(c0P,signalP))
n4RMSP = RMS(np.subtract(c4P,signalP))
n5RMSP = RMS(np.subtract(c5P,signalP))

n0RMS = RMS(np.subtract(c0,signal))
n1RMS = RMS(np.subtract(c1,signal))
n2RMS = RMS(np.subtract(c2,signal))
n3RMS = RMS(np.subtract(c3,signal))
n4RMS = RMS(np.subtract(c4,signal))
n5RMS = RMS(np.subtract(c5,signal))
n6RMS = RMS(np.subtract(c6,signal))

snrPAM = signalPRMS / np.array([n0RMSP,n0RMSP,n0RMSP])
snrPAMdB = 10 * np.log10(snrPAM)

snrQAM = signalRMS / np.array([n0RMS,n1RMS,n2RMS,n3RMS,n4RMS,n5RMS,n6RMS])
snrQAMdB = 10 * np.log10(snrQAM)

xP = np.array([500,10000,50000])
x = np.array([500,1000,2000,5000,10000,50000,100000])

plt.xlabel("Frequency (Hz)")
plt.xscale('log')
plt.yscale('log')
#plt.yticks([1.8,2,2.5])
plt.ylabel("SNR (dB)")
plt.title("A Plot of SNR against Frequency")
#plt.legend(("16QAM","4PAM"))

plt.plot(x, snrQAMdB)
plt.plot(xP, snrPAMdB)
plt.show()
