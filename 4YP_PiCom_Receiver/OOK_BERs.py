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




transmission_frequencies = [1,10,100,1000,10000,100000,1000000,10000000]

orig = list(open('OOK_DATA_INPUT_falling_edge.txt', 'r').read())


numchannel = len(transmission_frequencies)

# init rx lists
rx_lists = []
for i in range(numchannel):
    #ci = list(open('OOK_DATA_INPUT_100Hz.txt', 'r').read()) 
    ci = list(open("OOK_FALLING_" + str(transmission_frequencies[i]) + "kHz.txt", 'r').read())
    rx_lists.append(ci)
    print("Length: {}".format(len(ci)))

# init errors
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
  


