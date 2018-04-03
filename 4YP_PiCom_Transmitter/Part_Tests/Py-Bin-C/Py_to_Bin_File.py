import numpy as np

i = np.arange(256)*10**5
i.astype('uint32').tofile('data.bin')
print("Done")
