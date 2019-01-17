'''
Decode different encodings.
J. Potter
'''

numberofresults = 26
encoding = "NRZ" #from [NRZ, NRZI, RZI, Manchester]

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

def decode

for length in lengths:
    # init rx lists
    errs = []
    rx_lists = []
    j = 1
    while j < numberofresults+1:
        for i in range(len(lengths)):
            orig_padded = list(open('I{}.txt'.format(j), 'r').read())
            orig = Remove_Padding(orig_padded) 
            ci_padded = list(open("O{}.txt".format(j), 'r').read())
            ci = Remove_Padding(ci_padded)
            print("ci length before cut: {}".format(len(ci_padded)))
            ci = ci[:len(orig)]
            print("Original length: {}".format(len(orig)))
            print("Length: {}".format(len(ci)))
            err = 0
            for k, orig_data in enumerate(orig):
                if k < len(ci):
                    if not orig_data == ci[k]:
                        err += 1
                else: err += 1
            errs.append(err)
            print("Percentage error: {}".format((err/len(orig))*100))
        j += 1