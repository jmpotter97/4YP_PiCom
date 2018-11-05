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




transmission_frequencies = [1000,1000000,1000000000,10000000000]
lengths = [100,200,400,500,700]

#orig = list(open('OOK_DATA_INPUT_falling_edge.txt', 'r').read())


numchannel = len(lengths)

for frequency in transmission_frequencies:
    # init rx lists
    rx_lists = []
    for i in range(numchannel):
        orig = list(open('OOK_DATA_INPUT_{}_{}Hz.txt'.format(lengths[i],frequency), 'r').read())
        #ci = list(open('OOK_DATA_INPUT_100Hz.txt', 'r').read()) 
        ci = list(open("OUTPUT_OOK_" + str(lengths[i]) + "_" + str(frequency) + "Hz" + ".txt", 'r').read())
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

