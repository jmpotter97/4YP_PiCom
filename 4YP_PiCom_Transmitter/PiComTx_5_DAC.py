 # Using GPIO library for Raspberry Pi
from time import sleep
from subprocess import call
import paramiko

# Transmission frequency in Hz
transmit_freq = 5000
clock_pin = 18
data_pin = 4
transmission_type = "4PAM"


def pause():
	prPause = input("Pause, press <ENTER> to continue...")

	
def getDummyData():
    '''
    print("No transition")
    arr = ([1,0]*8)*1000
    
    print("Half transition")
    arr = ([1,0]*4+[0]*8)*1000
    '''
    print("Full transition WITH USLEEP(100)")
    arr = ([1,0]*4+[0,1]*4)*1000
    
    return arr


def getImageBytes(path):
        with open(path, 'rb') as f:
                out = f.read()
        return out


def chunks(l, n):

    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def Ssh_Start_Receiver():
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


def Encode_Error_Correction(data_list):
    ''' TO BE ADDED '''


def Convert_To_Data_Mask(data_list):
        # TODO: Change back to 2 bits for 4PAM not 256PAM
        data_string = ""
        if transmission_type == "4PAM":
            subdata = chunks(data_list,8)
            for byte in subdata:
                bin_str = ""
                for bit in byte:
                    bin_str += str(bit)
                if int(bin_str,2)<16:
                    data_string += '0' + hex(int(bin_str,2))[2:]
                else:
                    data_string += hex(int(bin_str,2))[2:]
            '''CHANGE EACH SET OF 2 BITS TO A LEVEL,
            EACH LEVEL TO A DAC VALUE BETWEEN 0 AND 255 (8-BIT DAC),
            EACH DAC VALUE TO A BIT-MASK FOR 8 PINS AS 2-SYM HEX
            data_string += %sub-mask for each level%'''
            return data_string
        else:
            print("Invalid transmission type!")

    
def Transmit_Data(data_string):
        print("Transmitting data")

        if transmission_type == "4PAM":
            return_code = call(["sudo","./PiTransmit_2", data_string])
        elif transmission_type == "4QAM":
            print("4QAM NO EXIST")
            # Doesn't exist yet
            # return_code = call(["./PiTransmit_2_QAM", "arg1", "arg2", "arg3"])
	    return_code = -1
        else:
            return_code = -1
	
	return_options = {-1 : "Invalid transmission type!",
			   0 : "Data transmission complete!",
			   1 : "Data transmission failed!",
			   2 : "GPIO INIT FAIL",	 # Add more failure codes
			   3 : "PiTransmit_2 ... Incorrect usage\n\nUsage: ./PiTransmit_2 transmit_data transmit_freq\n"}
			
	if return_code in return_options:
		print(return_options[return_code])
        else:
            print("Return code (time to execute)")
            print(return_code)
            t1 = return_code * (10**-6)
            print("Bit rate")
            print(str(t1/16000))
            print("Byte rate")
            print(str(t1/2000))
            print("Bit frequency")
            print(str(1/(t1/16000)))
            

#if __name__ == '__main__':
try:
    #receiver_started = Ssh_Start_Receiver()
    if 1:# receiver_started:
        input_stream = getDummyData()
        #input_stream  = getImageBytes('cat.png')
        
        # Encode_Error_Correction(input_stream)
        
        input_mask = Convert_To_Data_Mask(input_stream)
        sleep(2)
        Transmit_Data(input_mask)

    print("Finishing program")


except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\nError is: {}".format(e))

