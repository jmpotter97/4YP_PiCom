'''
Testing encoding scheme code.
J. Potter
'''
def NRZI(data):
    output = []
    previous_output = 0;
    for value in data:
        if value == 0:
            output.append(previous_output)
        if value == 1:
            if previous_output == 1:
                output.append(0)
                previous_output = 0
            else:
                if previous_output == 0:
                    output.append(1)
                    previous_output = 1
    return output

def RZI(data):
    output = []
    for value in data:
        if value == 0:
            output.append(1)
            output.append(0)
        if value == 1:
            output.append(0)
            output.append(0)
    return output

def Manchester(data):
    output = []
    for value in data:
        if value == 0:
            output.append(0)
            output.append(1)
        if value == 1:
            output.append(1)
            output.append(0)
    return output

data = [1,1,1,1,0,0,1,1,0,0,1,1,1,1]
print(NRZI(data))
print(RZI(data))
print(Manchester(data))