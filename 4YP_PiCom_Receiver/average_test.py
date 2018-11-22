

def Average(values):
    total = 0
    for value in values:
        total = total + value
    total = (total+1)/(len(values)+1)
    total = int(round(total))
    return total

arrays = []
arrays.append([0,0,0,0,0,0,0,0,0,1])
arrays.append([0, 0, 1])
arrays.append([0, 0, 0])
arrays.append([0, 1, 0, 1])
arrays.append([0, 0, 0, 1, 1, 1])
arrays.append([0, 0, 1, 0, 1, 1, 1])
arrays.append([0,0,0,0,0,0,1,1,1,1,1])

for array in arrays:
    print(Average(array))
