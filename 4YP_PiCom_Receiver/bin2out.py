import numpy as np

i = np.fromfile('data_masks.bin', dtype='uint32')
DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [14, 15, 18, 17, 27, 22, 23, 24]

def pam4(masks):
    out = np.zeros(masks.size//4, dtype='uint8')
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
    print("Attenuation = {}\n".format( (255-(highest-lowest)) / 255 ))
    # SYMB
    for i in range(masks.size):
        if highest != 255 and highest != lowest and highest != 0:
            masks[i] = round((masks[i]-lowest)*255/(highest-lowest))
        # Masks are 8-bit and full-range
        # Maximum likelihood reconstruction of masks to symbols:
        if masks[i] < 0.5*85:
            masks[i] = 0
        elif 0.5*85 < masks[i] < 1.5*85:
            masks[i] = 1
        elif 1.5*85 < masks[i] < 2.5*85:
            masks[i] = 2
        else:
            masks[i] = 3
    return masks[:500]
    # OUT
    for i in range(out.size):
        for s in range(4):
            out[i] |= (2 ** (2*s)) * masks[4*i+3-s]
    return out


print(pam4(i))
