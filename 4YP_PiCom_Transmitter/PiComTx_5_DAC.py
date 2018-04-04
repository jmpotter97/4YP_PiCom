import numpy as np
import imageio as io
from time import sleep
from subprocess import call
import paramiko

TRANSMISSION_TYPES = ["4PAM", "256PAM"] #, "16QAM", "OFDM"] to be added
TRANSMISSION_TYPE = "4PAM"
DATA_PATH = "data_masks.bin"
DATA_INV_PATH = "data_masks_inv.bin"

DAC_PINS_1, DAC_PINS_2 = [5, 6, 13, 19, 26, 21, 20, 16], \
                         []
DAC_MASK_1, DAC_MASK_2 = 0, 0

for pin1, pin2 in zip(DAC_PINS_1, DAC_PINS_2):
	DAC_MASK_1 |= (1<<pin1)
	DAC_MASK_2 |= (1<<pin2)

''' DAC_MASK_# is a bit mask of the GPIO pins which that DAC uses,
    expressed here in the form b7,...,b0. This is XOR'd with the
    gpioWrite_Bits_0_31_Set bit-mask (to invert for gpioWrite_Bits_0_31_Clear)
'''

# Nice to use for debugging
def pause(string = ""):
        if string != "":
                string += "\n"
        input(string+"Pause, press <ENTER> to continue...")


def getDummyData():
    '''
    print("No transition")
    arr = ([1,0]*8)*1000

    print("Half transition")
    arr = ([1,0]*4+[0]*8)*1000
    '''
    print("Full transition")
    arr = ([1, 0]*4+[0, 1]*4)*1000

    return np.array(arr, dtype=np.int)


def getImageBytes(path):
    # PIL modes - RGB, L (greyscale)
    img = io.imread(path, pilmode = "L")
    size = img.size
    
    return img.reshape(size)


def Ssh_Start_Receiver():
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    # Update command for new file name
    command = "sudo python3 /home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/PiComRx_5_DAC.py"
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
    '''
    INPUT goes through a number of stages:
    SYMB - CHANGE EACH BYTE TO A (NUMBER OF) LEVEL(S) (0,1,2,3 for 4PAM),
            I AND Q FOR QAM,
    DAC  - EACH LEVEL TO A DAC VALUE BETWEEN 0 AND 255 (8-BIT DAC),
            DAC1 AND DAC2 FOR QAM
    MASK - EACH DAC (PAIR) VALUE TO A BIT-MASK FOR 8/16 PINS IN BANK
            Expand dac values onto 32-bit mask
            mask = F(dac);
            WHERE F() MAPS THE 8-BIT DAC VALUE TO THE 32-BIT MASK
    '''
    
    if TRANSMISSION_TYPE == "256PAM":
        # 1 SYMB/byte
        # DAC = INPUT
        # MASK
        mask = np.zeros(data_list.size, dtype='uint32')
        for i, DAC_level in enumerate(data_list):
            if i%25000 == 0:  #Stats
                print("Symbol - {}".format(i))
            mask32 = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask 
                if (1<<(7-j)) & DAC_level:
                    mask32 |= (1<<pin)
            mask[i] = mask32
        return mask
    
    elif TRANSMISSION_TYPE == "4PAM":
        # 4 SYMB/byte
        symb = np.zeros(4*data_list.size, dtype=np.uint32)
        for i, byte in enumerate(data_list):
            if i%25000 == 0:  #Stats
                print("Symbol - {}".format(i))
            for s in range(4):
                symb[4*i+3-s] = (((1<<(2*s+1)) | (1<<(2*s))) & byte) \
                               // (2**(2*s))                            
        # DAC
        symb *= 85  # dac = symb * 85 --> 0, 85, 170, 255
        # MASK
        mask = np.zeros_like(symb)
        for i, DAC_level in enumerate(symb):
            if i%25000 == 0:  #Stats
                print("Mask - {}".format(i))
            mask32 = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask 
                if (1<<(7-j)) & DAC_level:
                    mask32 |= (1<<pin)
            mask[i] = mask32
        return mask
    elif TRANSMISSION_TYPE == "16QAM":
        # TODO: ADD ANOTHER FOR SECOND DAC
        # enumerate(DAC_PINS_1+DAC_PINS_2)
        print("TODO: QAM")
    else:
        print("Invalid transmission type!")


def Invert_Mask(mask):
    if "PAM" in TRANSMISSION_TYPE:
        return mask ^ DAC_MASK_1
    else:
        return mask ^ (DAC_MASK_1 | DAC_MASK_2)


def Save_To_File(mask, path):
    mask.astype('uint32').tofile(path)


def Transmit_Data():
    print("Transmitting data")
        
    if TRANSMISSION_TYPE in TRANSMISSION_TYPES:
        return_code = 4#call(["sudo","./PiTransmit_3"])
    else:
        return_code = -1
        
    return_options = {-1: "Invalid transmission type!",
                      0: "Data transmission complete!",
                      1: "Data transmission failed!",
                      2: "GPIO INIT FAIL",         # TODO: Add more failure codes?
                      3: "PiTransmit_3 ... Incorrect usage\n\nUsage: sudo ./PiTransmit_3\n",
                      4: "Mask file and Invert mask file different lengths."}

    if return_code in return_options:
        print(return_options[return_code])
    else:
        print("Unrecognised return code")
        
    '''
    TEST CODE WHEN RETURNING 'TIME TO EXECUTE TRANSMITTER'
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
    '''

# try when debugging to catch errors, not necessary for use
try:
    pause("Start")
    # receiver_started = Ssh_Start_Receiver()
    if 1:  # receiver_started:
        # input_stream = getDummyData()
        # input_stream = bin_array_to_bytes()
        input_stream = getImageBytes('cat.png')
        print("Input stream length: {}".format(input_stream.shape))

        # TODO: Encode_Error_Correction(input_stream)

        print("Converting data to masks...")
        input_mask = Convert_To_Data_Mask(input_stream)
        input_mask_inv = Invert_Mask(input_mask)
        print("Saving data as masks...")
        Save_To_File(input_mask, DATA_PATH)
        Save_To_File(input_mask_inv, DATA_INV_PATH)
        
        Transmit_Data()
    else:
        print("Receiver never started")

    print("Finishing program")


except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\nError is: {}".format(e))

