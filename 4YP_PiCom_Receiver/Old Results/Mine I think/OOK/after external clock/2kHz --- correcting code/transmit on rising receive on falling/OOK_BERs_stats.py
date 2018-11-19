'''
J. Potter based on code by C. Eadie

A function to evaluate the frequency/BER characteristics of the OOK set-up after reading in the input sequence and output

'''

'''
import matplotlib.pyplot as plt



def plot_frequency_response(percentage_BERs, transmission_frequencies):
    x = transmission_frequencies
    y = percentage_BERs
    fig = plt.figure(1, figsize=(8,6))
    ax = plt.subplot(1,1,1)
    ax.plot(x,y)
    ax.set_xlabel("Frequency (kHz)")
    ax.set_ylabel("BER (%)")
    ax.set_title("Plot of OOK Frequency Response")
    fig.show()
'''

numberofresults = 8
transmission_frequencies = [100]
lengths = [100,1000,10000]
numchannel = len(lengths)

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

for length in lengths:
    # init rx lists
    errs = []
    rx_lists = []
    j = 1
    while j < numberofresults+1:        
        orig_padded = list(open('I{}.txt'.format(length), 'r').read())
        orig = Remove_Padding(orig_padded) 
        ci_padded = list(open("O{}_{}.txt".format(j,length), 'r').read())
        ci = Remove_Padding(ci_padded)
        print(len(ci_padded))
        print("Length: {}".format(len(ci)))
        err = 0
        for i, orig_data in enumerate(orig):
            if i < len(ci):
                if not bool(orig_data) == bool(ci[i]):
                    err += 1
            else: err += 1
        errs.append(err)
        print("Percentage error: {}".format((err/len(orig))*100))
        j += 1
# init errors
'''
errs = []
for i in range(numchannel):
    errs.append(0)

check_first_sync = []
sync_error_position = []

for j, rx_list in enumerate(rx_lists):
    for i, orig_data in enumerate(orig):
        if i < len(rx_list):
            if not bool(orig_data) == bool(rx_list[i]):
                errs[j] += 1
        else: errs[j] += 1

percentage_BERs = []
for i, BER in enumerate(errs):
    #print("Bit Error {} = {}\n".format(str(transmission_frequencies[i])+"kHz",BER))
    percentage_BER = (BER/len(orig))*100
    print("Percentage Bit Error {} = {}\n".format(str(transmission_frequencies[i])+"kHz",percentage_BER))
    percentage_BERs.append(percentage_BER)
print(sync_error_position)

#plot_frequency_response(percentage_BERs, transmission_frequencies)
  
'''

