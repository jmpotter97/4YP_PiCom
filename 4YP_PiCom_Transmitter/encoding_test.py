'''
J. Potter

Testing line coding scheme code is outputting correctly.
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

def decode_NRZI(result):
    data = []
    if result[0] == 0:
        data.append(1)
        previous_result = 0
    else:
        data.append(0)
        previous_result = 1
    for bit in result[1:]:
        if previous_result == 0:
            if bit == 0:
                data.append(0)
                previous_result = 0
            else:
                data.append(1)
                previous_result = 1
        else: 
            if bit == 0:
                data.append(1)
                previous_result = 0
            else:
                data.append(0)
                previous_result = 1
    return(data)

def decode_RZI(result):
    data = []
    for bit in result[::2]:
        if bit == 0:
            data.append(1)
        else:
            data.append(0)
    return(data)

def decode_Manchester(result):
    data = []
    for bit in result[::2]:
        if bit == 0:
            data.append(0)
        else:
            data.append(1)
    return(data)



data = [1,1,1,1,0,0,1,1,0,0,1,1,1,1]
print(data)

'''
x = NRZI(data)
print(x)
y = decode_NRZI(x)
print(y)
'''
'''
x = RZI(data)
print(x)
y = decode_RZI(x)
print(y)
'''
x = Manchester(data)
print(x)
y = decode_Manchester(x)
print(y)