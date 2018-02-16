# Using GPIO library for Raspberry Pi
import RPi.GPIO as GPIO
from time import sleep
import threading
import paramiko

# Transmission frequency in Hz
transmit_freq = 100

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

def Prep_Binary_Data(dataList):
    if not all(b == 0 or b == 1 for b in dataList):
        print("Data to transmit is not binary, stopping transmission")
    else:
        # Add excess continuous value padding
        print("SIZE OF INPUT = {}".format(len(dataList)))
        pad_bits=0
        for i in range(5,len(dataList)):
            if dataList[i+pad_bits-5:i+pad_bits] == [0]*5:
                dataList.insert(i+pad_bits,1)
                pad_bits = pad_bits + 1
            elif dataList[i+pad_bits-5:i+pad_bits] == [1]*5:
                dataList.insert(i+pad_bits,0)
                pad_bits = pad_bits + 1
        # Adding end start and end of transmission padding to data
        dataList[:0] = [1]*8+[0]
        dataList[-1:] = [0]+[1]*8
        print("SIZE OF PADDED INPUT = {}".format(len(dataList)))
        return dataList

def Transmit_Binary_Data(dataList):
        print("Transmitting data")
        ############################# STILL NEED TIMING#############
        for b in dataList:
            GPIO.output(4, b)
            sleep(1/transmit_freq)
        GPIO.output(4, GPIO.LOW)
        print("Data transmission complete!")

try:
    # Use BCM numbering standard
    GPIO.setmode(GPIO.BCM);
    # Set BCM pin 4 as an output
    GPIO.setup(4, GPIO.OUT, initial=GPIO.LOW)

    receiver_started = Ssh_Start_Receiver()
    if receiver_started:
        input_stream = ([1,0]*5 + [1]*10)*20
        Prep_Binary_Data(data)
        sleep(2)
        Transmit_Binary_Data(input_stream)

    print("Finishing program")
        
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\nError is: {}".format(e))
finally:
    GPIO.cleanup()
