'''
A function to decode different line codings and analyse BERs of outputs of receiver.
J. Potter
'''

numberofresults = 50
encoding = "NRZI" #from [NRZ, NRZI, RZI, Manchester]

def Remove_Padding(data):
    j = 0
    while int(data[0]) == 1 and j < 49:
        data = data[1:]
        j += 1
    data = data[1:]
    while int(data[-1]) == 0:
        del data[-1]
    del data[-1]
    return data

def decode_NRZI(result):
    data = []
    if int(result[0]) == 0:
        data.append(0)
        previous_result = 0
    else:
        data.append(1)
        previous_result = 1
    for bit in result[1:]:
        if previous_result == 0:
            if int(bit) == 0:
                data.append(0)
                previous_result = 0
            else:
                data.append(1)
                previous_result = 1
        else: 
            if int(bit) == 0:
                data.append(1)
                previous_result = 0
            else:
                data.append(0)
                previous_result = 1
    return(data)

def decode_RZI(result):
    data = []
    for bit in result[::2]:
        if int(bit) == 0:
            data.append(1)
        else:
            data.append(0)
    return(data)

def decode_Manchester(result):
    data = []
    for bit in result[::2]:
        if int(bit) == 0:
            data.append(0)
        else:
            data.append(1)
    return(data)

j = 1
while j < numberofresults+1:
    orig_padded = list(open('I{}.txt'.format(j), 'r').read())
    orig = Remove_Padding(orig_padded) 
    orig_encoded_padded = list(open('I_ENCODED{}.txt'.format(j), 'r').read())
    orig_encoded = Remove_Padding(orig_encoded_padded) 
    result_encoded_padded = list(open("O{}.txt".format(j), 'r').read())
    result_encoded = Remove_Padding(result_encoded_padded)
    if encoding == "NRZ":
        result = result_encoded
    elif encoding == "NRZI":
        result = decode_NRZI(result_encoded)
    elif encoding == "RZI":
        result = decode_RZI(result_encoded)
    elif encoding == "Manchester":
        result = decode_Manchester(result_encoded)
    print("Original length: {}".format(len(orig)))
    print("Length: {}".format(len(result)))
    err = 0
    err_encoded = 0
    for k, orig_data in enumerate(orig):
        if k < len(result):
            if not int(orig_data) == result[k]:
                err += 1
        else: err += 1
    for k, orig_encoded_data in enumerate(orig_encoded):
        if k < len(result_encoded):
            if not int(orig_encoded_data) == int(result_encoded[k]):
                err_encoded += 1
        else: err_encoded += 1
    print("Percentage error of transmission (encoded): {}".format((err_encoded/len(orig_encoded))*100))
    print("Percentage error of message (decoded): {}\n".format((err/len(orig))*100))
    j += 1
