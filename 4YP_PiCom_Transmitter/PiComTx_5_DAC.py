 # Using GPIO library for Raspberry Pi
from time import sleep
from subprocess import call
import threading
import paramiko

# Transmission frequency in Hz
transmit_freq = 100
clock_pin = 18
data_pin = 4

def Ssh_Start_Receiver():
    print("\n---SSH lock---")
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
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

def Transmit_Data(data_list, transmission_type):
        print("Transmitting data")

        if transmission_type == "4PAM":
            return_code = call(["./PiTransmit_2", "arg1", "arg2", "arg3"])
        elif transmission_type == "4QAM":
            #return_code = call(["./PiTransmit_2", "arg1", "arg2", "arg3"])
        else:
            return_code = -1

        if return_code == 0:
            print("Data transmission complete!")
        elif return_code == -1:
            print("Invalid transmission type!")
        elif return_code == 1:
            print("Data transmission failed!") # Add more failure codes

try:

    receiver_started = Ssh_Start_Receiver()
    if receiver_started:
        input_stream = ([1,0]*5 + [1]*10)*20
        Prep_Binary_Data(input_stream)
        sleep(2)
        Transmit_Data(input_stream,"4PAM")

    print("Finishing program")
        
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\nError is: {}".format(e))
