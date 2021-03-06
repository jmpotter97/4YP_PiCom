'''
J. Potter

A function to evaluate the frequency/BER characteristics of the OOK set-up after reading in the input sequence and output
'''

#Plot Results
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

transmission_frequencies = [100]
lengths = [1000]
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

for frequency in transmission_frequencies:
    # init rx lists
    rx_lists = []
    for i in range(numchannel):
        orig_padded = list(open('OOK_DATA_INPUT_{}_{}Hz.txt'.format(lengths[i],frequency), 'r').read())
        orig = Remove_Padding(orig_padded)
        #ci = list(open('OOK_DATA_INPUT_100Hz.txt', 'r').read()) 
        ci_padded = list(open("OUTPUT_OOK_" + str(lengths[i]) + "_" + str(frequency) + "Hz" + ".txt", 'r').read())
        print("Padded Length: {}".format(len(ci_padded)))
        ci = Remove_Padding(ci_padded)
        #rx_lists.append(ci)
        print("Length: {}".format(len(ci)))
        print("Frequency: {}".format(frequency))
        err = 0
        for i, orig_data in enumerate(orig):
            if i < len(ci):
                if not bool(orig_data) == bool(ci[i]):
                    err += 1
            else: err += 1
        print("Percentage error: {}".format((err/len(orig))*100))

