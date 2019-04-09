'''
J. Potter

A function to evaluate the frequency/BER characteristics of the OOK set-up after reading in the input sequence and output
'''

#Plot results
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
numberofresults = 20
transmission_frequencies = [100]
lengths = [100]

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
    total_BERs = 0
    for error in errs:
        total_BERs = total_BERs + error
    average_BER = total_BERs/len(errs)
    print('Average BER: {}'.format(average_BER))

