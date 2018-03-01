 # Using GPIO library for Raspberry Pi
from time import sleep
from subprocess import call
import threading
#import paramiko

# Transmission frequency in Hz
transmit_freq = 5000
clock_pin = 18
data_pin = 4
transmission_type = "4PAM"

def Ssh_Start_Receiver():
    print("\n---SSH lock---")
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    # Update command for new file name
    command = "sudo python3 /home/pi/Documents/PiComRx_3_Clocked.py"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to host
        print("Connecting to {}".format(host))
        ssh.connect(host, username=uname, password=pword)
        print("Connected!")
    except Exception as e:
        print("Exception raised attempting to connect to ssh host",
              "\nError is: {}".format(e))

    if ssh.get_transport().is_active():
        print("Executing command to start comReceiver")
        stdin, stdout, stderr = ssh.exec_command(command)
        
        sleep(5)
        print("Closing ssh connection\n")
        ssh.close()
        return True
    else:
        print("Closing unsuccessful ssh connection\n")
        ssh.close()
        return False

def Prep_Binary_Data(data_list):
    if not all(b == 0 or b == 1 for b in data_list):
        print("Data to transmit is not binary, stopping transmission")
    else:
        # Add excess continuous value padding
        print("SIZE OF INPUT = {}".format(len(data_list)))
        pad_bits=0
        for i in range(5,len(data_list)):
            if data_list[i+pad_bits-5:i+pad_bits] == [0]*5:
                data_list.insert(i+pad_bits,1)
                pad_bits = pad_bits + 1
            elif data_list[i+pad_bits-5:i+pad_bits] == [1]*5:
                data_list.insert(i+pad_bits,0)
                pad_bits = pad_bits + 1
        # Adding end start and end of transmission padding to data
        data_list[:0] = [1]*7+[0]
        data_list[-1:] = [0]+[1]*7
        print("SIZE OF PADDED INPUT = {}".format(len(data_list)))
        return data_list

def Encode_Error_Correction(data_list):
    ''' TO BE ADDED '''

def Convert_To_Data_Mask(data_list):
    ''' TO BE ADDED '''
    '''
        data_string = ""
        if transmission_type == "4PAM":
            CHANGE EACH SET OF 2 BITS TO A LEVEL,
            EACH LEVEL TO A DAC VALUE BETWEEN 0 AND 255 (8-BIT DAC),
            EACH DAC VALUE TO A BIT-MASK FOR 8 PINS AS 2-SYM HEX
            data_string += %sub-mask for each level%
            return data_string
        else:
            print("Invalid transmission type!")
    '''
    
def Transmit_Data(data_string):
        print("Transmitting data")

        if transmission_type == "4PAM":
            return_code = call(["./PiTransmit_2", data_string, str(transmit_freq)])
        elif transmission_type == "4QAM":
            print("4QAM NO EXIST")
            # Doesn't exist yet
            # return_code = call(["./PiTransmit_2_QAM", "arg1", "arg2", "arg3"])
        else:
            return_code = -1

        if return_code == 0:
            print("Data transmission complete!")
        elif return_code == -1:
            print("Invalid transmission type!")
        elif return_code == 1:
            print("Data transmission failed!") # Add more failure codes

try:

    #receiver_started = Ssh_Start_Receiver()
    if 1:# receiver_started:
        input_stream = ([1,0]*5 + [1]*10)*20
        #input_stream will be from an image
        Prep_Binary_Data(input_stream)
        # Encode_Error_Correction(input_stream)
        
        # string input_mask = Convert_To_Data_Mask(input_stream)
        sleep(2)
        Transmit_Data(input_mask)

    print("Finishing program")
        
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\nError is: {}".format(e))
