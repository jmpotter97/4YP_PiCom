# Using GPIO library for Raspberry Pi
import RPi.GPIO as GPIO
from time import sleep
import threading
import paramiko

# Transmission frequency in Hz
transmit_freq = 100

def ssh_start_receiver():
    threadLock.acquire()
    print("\n---SSH lock---")
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    command = "sudo python3 /home/pi/Documents/comReceiver.py"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to host
        print("Connecting to {}".format(host))
        ssh.connect(host, username=uname, password=pword)
        print("Connected!")
    
    except paramiko.AuthenticationException:
        print("Authentication to failed!\n")
    except paramiko.SSHException:
        print("Error making the connection or establishing connection")
    except paramiko.BadHostKeyException:
        print("Bad host key (Host not found)")
    except:
        print("Error in ssh connection")

    if ssh.get_transport().is_active():
        print("Executing command to start comReceiver")
        stdin, stdout, stderr = ssh.exec_command(command)
        print("---SSH unlock---\n")
        threadLock.release()
        for line in iter(stdout.readline, ""):
            print("... "+line, end="")
        print("Closing ssh connection\n")
        ssh.close()
    else:
        print("Closing unsuccessful ssh connection\n")
        ssh.close()
        print("---SSH unlock---")
        threadLock.release()

def transmit_binary_data(dataList):
    if not all(b == 0 or b == 1 for b in dataList):
        print("Data to transmit is not binary, stopping transmission")
    else:
        # Add excess continuous value padding
        for i in range(5,len(dataList)):
            if dataList[i-5:i] == [0]*5:
                dataList.insert(i,1)
            elif dataList[i-5:i] == [1]*5:
                dataList.insert(i,0)
        # Adding padding to data
        dataList[:0] = [1]*8
        dataList[-1:] = [1]*8
        print("SIZE OF INPUT = {}".format(len(dataList)))
        print("Transmitting data")
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

    threadLock = threading.Lock()
    receiver = threading.Thread(target=ssh_start_receiver)
    receiver.start()
    threadLock.acquire()
    print("---Data lock---")
    if receiver.isAlive():
        data = [1,0]*10000#([0,1]*5 + [1]*10 + [0,1]*5)*20
        sleep(2)
        transmit_binary_data(data)
    print("---Data unlock---\n")
    threadLock.release()

    print("Waiting for receiver to close, logs below...\n")
    receiver.join()
    print("Finishing program")
        
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
    
finally:
    GPIO.cleanup()
