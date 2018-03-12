import numpy as np
import matplotlib.pyplot as plt

with open('cat.png', 'rb') as f:
    cat = f.read()
    
output_cat = []
for byte in cat:
    output_cat.append(byte)
#print("Length is {}".format(len(output_cat)))

#print(output_cat[69998:70005])

#for i,data in enumerate(output_cat[70000:105000]):
#    output_cat[i+70000] = 0

#print("And after the nonsense")
#print(output_cat[69998:70005])

output_cat[69998]=0

with open('output_cat.png', 'wb') as f:
    f.write(bytes(output_cat))
        
print("Done!!!")
