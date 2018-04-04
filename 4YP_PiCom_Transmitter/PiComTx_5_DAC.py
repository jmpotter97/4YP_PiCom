import numpy as np
import imageio as io
from time import sleep
from subprocess import call
import paramiko

TRANSMISSION_TYPE = "4PAM"
DATA_PATH = "data_masks.bin"
DATA_INV_PATH = "data_masks_inv.bin"

DAC_PINS_1, DAC_PINS_2 = [5, 6, 13, 19, 26, 21, 20, 16], \
                         []
DAC_MASK_1, DAC_MASK_2 = 0, 0

for pin1, pin2 in zip(DAC_PINS_1, DAC_PINS_2):
	DAC_MASK_1 |= (1<<pin1)
	DAC_MASK_2 |= (1<<pin2)

''' DAC_BITS is a bit mask of the GPIO pins which that DAC uses,
    expressed here in the form b7,...,b0. This is XOR'd with the
    gpioWrite_Bits_0_31_Set bit mask (invert for gpioWrite_Bits_0_31_Clear)

    const int sub_mask_size = 2 * num_of_DAC;
	const int mask_size = strlen(transmit_data) / sub_mask_size;
    char format[] = "%_x";			// %2x for one DAC, %4x for two DAC's
    format[1] = sub_mask_size + 48;	// +48 for ASCII value of number

	uint32_t* transmit_data_mask = calloc(mask_size, sizeof(uint32_t));
	uint32_t* transmit_data_inv_mask = calloc(mask_size, sizeof(uint32_t));
	for(int i = 0; i<mask_size; i++) {
		// Move each sub-mask into an int in transmit_data_mask array
		sscanf((transmit_data + sub_mask_size*i),format,&transmit_data_mask[i]);
		// Expand sub-mask into 32-bit mask
		// transmit_data_mask[i] = F(transmit_data_mask[i]);
		// WHERE F() MAPS THE 8-BIT SUB-MASK TO THE 32-BIT MASK
		int mask32 = 0;
		for(int j = 0; j<8; j++) {	// TODO: ADD ANOTHER FOR SECOND DAC
			// If each bit in binary exists, include it in 32-bit mask
			if((1<<(7-j)) & transmit_data_mask[i]) {
				mask32 |= (1<<DAC_1_bits[j]);
			}
		}
		transmit_data_mask[i] = mask32;
		transmit_data_inv_mask[i] = mask32 ^ DAC_1_mask;
	}

    '''


def pause(string = ""):
        if string != "":
                string += "\n"
        input(string+"Pause, press <ENTER> to continue...")

pause('lol')
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
    command = "sudo python3 /home/pi/Documents/PiComRx_5_DAC.py"
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
    '''
    
    # TODO: Change back to 2 bits for 4PAM when not 256PAM
    if TRANSMISSION_TYPE == "256PAM":
        # 1 SYMB/byte
        # DAC = INPUT
        # MASK
        mask = np.zeros(data_list.size, dtype='uint32')
        for i, DAC_level in enumerate(data_list):
            '''
            Expand dac values onto 32-bit mask
            mask = F(dac == data_list here);
            WHERE F() MAPS THE 8-BIT DAC VALUE TO THE 32-BIT MASK
            '''
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
            for s in range(4):
                symb[i+s] = ((1<<(2*s+1)) | (1<<(2*s))) / (2**s)
        # DAC
        dac = symb * 64 - 1
        # MASK
        mask = np.zeros_like(dac)
        for i, DAC_level in enumerate(dac):
            '''
            Expand dac values onto 32-bit mask
            mask = F(dac == data_list here);
            WHERE F() MAPS THE 8-BIT DAC VALUE TO THE 32-BIT MASK
            '''
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


def Transmit_Data(data_string):
    print("Transmitting data")
        
    # if "PAM" in TRANSMISSION_TYPE
    if TRANSMISSION_TYPE == "4PAM":
        return_code = call(["sudo","./PiTransmit_2", data_string])
    elif TRANSMISSION_TYPE == "4QAM":
        print("4QAM NO EXIST")
        # Doesn't exist yet
        # return_code = call(["./PiTransmit_2_QAM", "arg1", "arg2", "arg3"])
        return_code = -1
    else:
        return_code = -1
        
    return_options = {-1: "Invalid transmission type!",
                      0: "Data transmission complete!",
                      1: "Data transmission failed!",
                      2: "GPIO INIT FAIL",         # Add more failure codes
                      3: "PiTransmit_2 ... Incorrect usage\n\nUsage: ./PiTransmit_2 transmit_data\n"}

    if return_code in return_options:
        print(return_options[return_code])
        
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


#try:
# receiver_started = Ssh_Start_Receiver()
if 1:  # receiver_started:
    # input_stream = getDummyData()
    # input_stream = bin_array_to_bytes()
    input_stream = getImageBytes('cat.png')
    print("Input stream length: {}".format(input_stream.shape))

    # TODO: Encode_Error_Correction(input_stream)

    input_mask = Convert_To_Data_Mask(input_stream)
    input_mask_inv = Invert_Mask(input_mask)

    Save_To_File(input_mask, DATA_PATH)
    Save_To_File(input_mask_inv, DATA_INV_PATH)
    sleep(2)
    #Transmit_Data(DATA_PATH)

print("Finishing program")


#except KeyboardInterrupt:
#    print("\nExiting program on keyboard interrupt")
#except Exception as e:
#    print("\nExiting program on unexpected error\nError is: {}".format(e))

