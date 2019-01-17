'''
Decode different encodings and analyse BERs.
J. Potter
'''

numberofresults = 26
encoding = "Manchester" #from [NRZ, NRZI, RZI, Manchester]

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

errs = []
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
    print("result length before cut: {}".format(len(result)))
    print("Original length: {}".format(len(orig)))
    print("Length: {}".format(len(result)))
    err = 0
    err_encoded = 0
    for k, orig_data in enumerate(orig):
        if k < len(result):
            if not orig_data == result[k]:
                err += 1
        else: err += 1
    errs.append(err)
    for k, orig_encoded_data in enumerate(orig_encoded):
        if k < len(result_encoded):
            if not orig_encoded_data == result_encoded[k]:
                err_encoded += 1
        else: err_encoded += 1
    errs.append(err_encoded)
    print("Percentage error of transmission (encoded): {}".format((err_encoded/len(orig_encoded))*100))
    print("Percentage error of message (decoded): {}\n".format((err/len(orig))*100))
    j += 1