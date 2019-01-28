'''
J. Potter based on code by C. Eadie

A function to evaluate the frequency/BER characteristics of the OOK set-up

OOK has been integrated from the previous versions, uses different pins and runs
using RPi.GPIO and python arrays instead of a C executable (pigpio) and NumPy arrays
'''

import numpy as np
import paramiko
from time import sleep

'''---------------------------   On-Off Keying   ---------------------------'''
def Add_Padding(unpadded_data):
    data = []
    # add pattern of 49 1s terminated by a 0, data, 1 followed by 49 0s
    for i in range(49):
        data.append(1)
    data.append(0)
    for i in unpadded_data:
        data.append(i)
    data.append(1)
    for i in range(49):
        data.append(0)
    return data

def Get_OOK_Data(length):
    unpadded_data = []
    for i in range(int(length)):
        value = int(np.random.randint(2, size=1))
        unpadded_data.append(value)
    return unpadded_data

def Transmit_Binary_Data(data_list,OOK_TRANS_FREQ):
    import RPi.GPIO as GPIO
    overclocking = 1
    try:
        # Use BCM numbering standard
        GPIO.setmode(GPIO.BCM);
        CLK_PIN = 20
        DATA_PIN = 21
        # Set BCM pin 4 as an output
        GPIO.setup(DATA_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(CLK_PIN, GPIO.OUT, initial=GPIO.LOW)#initial=GPIO.LOW)
        half_clock_clock = 1 / ((2 * OOK_TRANS_FREQ)*overclocking) #overclock - number of clock cycles per bit       
        half_clock_data = 1 / (2 * OOK_TRANS_FREQ)
        print("Transmitting data")

        counter = 0

        for b in data_list:
            #GPIO.wait_for_edge(CLK_PIN, GPIO.RISING, timeout=1000)
            GPIO.output(DATA_PIN, b)

            '''while counter < overclocking:
                #overclocking
                GPIO.wait_for_edge(CLK_PIN, GPIO.RISING, timeout=1000)
                if counter == overclocking - 1:
                    counter = 0 
                    GPIO.output(DATA_PIN, b)
                    break
                counter += i'''

            #pi clock
            for i in range(overclocking):
                GPIO.output(CLK_PIN, GPIO.HIGH)            
                sleep(half_clock_clock)
                GPIO.output(CLK_PIN, GPIO.LOW)
                sleep(half_clock_clock)
        GPIO.output(DATA_PIN, GPIO.LOW)
        print("Data transmission complete!")        
    except KeyboardInterrupt:
        print("\nExiting program on keyboard interrupt")
    except Exception as e:
        print("\nExiting program on unexpected error\nError is: {}".format(e))
    finally:
        print("Cleaning up GPIOs")
        GPIO.cleanup()

'''--------------------------------   SSH   --------------------------------'''

def Ssh_Start_Receiver(mask_length):
    print("Starting Receiver")    
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    TRANSMISSION_TYPE = "OOK"
    # Update command for new file name
    command = "sudo python3 " + \
              "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/PiComRx_5_DAC.py" + \
              " " +str(mask_length) + " " +str(TRANSMISSION_TYPE)
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to host
        print("Connecting to {}".format(host))
        ssh.connect(host, username=uname, password=pword)
        print("Connected!")
    except Exception as e:
        print("Exception raised attempting to connect to ssh host",
              "\n\tError is: {}".format(e))
        return False
    if ssh.get_transport().is_active():
        print("Executing command to start comReceiver")
        stdin, stdout, stderr = ssh.exec_command(command)

        print("Receiver started, closing ssh connection\n")
        ssh.close()
        return True
    else:
        print("Closing unsuccessful ssh connection\n")
        ssh.close()
        return False

def Fetch_Receiver_Logs():
    print("\nFetching LOGS from receiver...")    
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    # Print LOGS to output
    command = "cat /home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/LOGS.txt"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to host
        print("Connecting to {}".format(host))
        ssh.connect(host, username=uname, password=pword)
        print("Connected!")
    except Exception as e:
        print("Exception raised attempting to connect to ssh host",
              "\n\tError is: {}".format(e))
    if ssh.get_transport().is_active():
        channel = ssh.invoke_shell()
        stdin, stdout, stderr = channel.send(command)
        '''if ssh.get_transport().is_active():
        stdin, stdout, stderr = ssh.exec_command(command)'''
        '''for line in iter(stdout.readline, ""):
        print(line, end="")'''
        ssh.close()
    else:
        print("Closing unsuccessful ssh connection\n")
        ssh.close()

'--------------------------------- Encoding -----------------------------------'
# Non-Return-To-Zero Inverted
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

# Return-To-Zero Inverted
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

# Manchester
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

'''---------------------------   Main   ---------------------------'''

def main():
    # Data stored as bits in Python lists
    # Transmitted using RPi.GPIO Python library      
    TRANSMISSION_TYPE = "OOK"
    transmission_frequencies = [1300]
    lengths = [1000,1000,1000,1000,1000,2000,2000,2000,2000,2000,3000,3000,3000,3000,3000,4000,4000,4000,4000,4000,5000,5000,5000,5000,5000,6000,6000,6000,6000,6000,7000,7000,7000,7000,7000,8000,8000,8000,8000,8000,9000,9000,9000,9000,9000,10000,10000,10000,10000,10000]
    encoding = "NRZI" #from [NRZ, NRZI, RZI, Manchester]
    global DATA_PATH
    global ENCODED_DATA_PATH
    counter = 1
    howmanytimesperlength = 0
    for length in lengths:
        for frequency in transmission_frequencies:
            DATA_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Transmitter/I{}.txt".format(counter)
            ENCODED_DATA_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Transmitter/I_ENCODED{}.txt".format(counter)
            OOK_input_stream = Get_OOK_Data(length)
            encoded_stream = []
            if encoding == "NRZ":
                encoded_stream = OOK_input_stream
            elif encoding == "NRZI":
                encoded_stream = NRZI(OOK_input_stream)
            elif encoding == "RZI":
                encoded_stream = RZI(OOK_input_stream)
            elif encoding == "Manchester":
                encoded_stream = Manchester(OOK_input_stream)
            else:
                print('Error: encoding is not of recognised type.')
                break
            encoded_stream = Add_Padding(encoded_stream)
            length = len(encoded_stream)
            with open(DATA_PATH,'w') as f:
                f.write("".join(str(i) for i in OOK_input_stream))
            with open(ENCODED_DATA_PATH,'w') as f:
                f.write("".join(str(i) for i in encoded_stream))
            receiver_started = Ssh_Start_Receiver(length)
            if receiver_started:
                print("About to transmit at {} Hz...".format(frequency))
                # Four seconds enough time to start receiver but not timeout
                sleep(4)
                Transmit_Binary_Data(encoded_stream,frequency)
                sleep(1) #make sure receiver will log result
            else:
                print("Receiver never started")
            print("\n Finishing transmitting at {} Hz".format(frequency))               
            counter += 1
    print("\nFinishing program")


# Use try when debugging to catch errors, not necessary for use
try:
    main()
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\n\tError is: {}".format(e))
