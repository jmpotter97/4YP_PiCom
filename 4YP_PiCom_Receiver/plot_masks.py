import numpy as np
import matplotlib.pyplot as plt

i = np.fromfile('data_masks.bin', dtype='uint32')
DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [14, 15, 18, 17, 27, 22, 23, 24]

def decode(masks):
    out = np.zeros(masks.size, dtype='uint8')
    for i, mask in enumerate(masks):
        val = 0
        for j, pin in enumerate(DAC_PINS_1):
            # If each bit in mask exists, include it in out
            if (1<<pin) & mask:
                val |= (1<<(7-j))
        out[i] = val
    return out

x = decode(i)
y = np.arange(x.size)

plt.plot(x,y)
plt.show()
