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




transmission_frequencies = [1]#,2,5,10,20,50,100,500,10000]

orig = list(open('OOK_DATA_INPUT_100Hz.txt', 'r').read())


numchannel = len(transmission_frequencies)

# init rx lists
rx_lists = []
for i in range(numchannel):
    ci = list(open('OOK_DATA_INPUT_100Hz.txt', 'r').read()) 
    #ci = list(open(str(i+1) + ".txt", 'r').read())
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
    print("Bit Error {} = {}\n".format(i+1,BER)) 
    percentage_BERs.append((BER/len(orig))*100)
print(percentage_BERs)
print(sync_error_position)

#plot_frequency_response(percentage_BERs, transmission_frequencies)
  


