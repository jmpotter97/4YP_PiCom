import numpy as np
import imageio as io
from time import sleep
from subprocess import run, PIPE
import paramiko
from sys import argv

# Used in Transmit_Binary_Data(): import RPi.GPIO as GPIO
# ... Only for OOK transmission which uses Python not C
# Used in Check_Input_Masks(): from RPiSim.GPIO import GPIO
# ... Only works in Windows to check masks work

'''
OOK has been integrated from the previous versions, uses different pins and runs
using RPi.GPIO and python arrays instead of a C executable (pigpio) and NumPy arrays

256PAM is too finely spaced to use successfully but is nice for setup

The Pi is not able to output negative voltages. Thus, Pulse Amplitude Modulation
uses the range 0 to Vmax not -Vmax to Vmax. Similarly, QAM uses a grid all in
the positive quadrant (0,1,2,3 not -3,-1,1,3). The same "negative" effect is still
achieved by using the "GROUND" of the multipliers (which are fully differential)
as Vmax/2 using a voltage divider. This means the sine and cos will be inverted
for the values 0 and 1 in the same way they would be for -3 and -1 and the
transmitted signal

J. Potter based on code by C. Eadie
'''

DATA_PATH = "data_masks.bin"
DATA_INV_PATH = "data_masks_inv.bin"
SYMB_RATE = 10                         # Symbol rate (Hz)
OOK_TRANS_FREQ = 1000
TRANSMISSION_TYPES = ["OOK","256PAM", "4PAM", "16QAM","basic_FSK","FSK"] #, "OFDM"] to be added
TRANSMISSION_TYPE = "OOK"
SIZE = 0

if len(argv) > 1:
        TRANSMISSION_TYPE = argv[1]

if TRANSMISSION_TYPE not in TRANSMISSION_TYPES:
    print("INVALID TRANSMISSION TYPE, EXITING")
    import sys
    sys.exit(1)
else:
    print("TRANSMISSION TYPE: {}".format(TRANSMISSION_TYPE))

DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [14, 15, 18, 17, 27, 22, 23, 24]
DAC_MASK_1, DAC_MASK_2 = 0, 0
for pin1 in DAC_PINS_1:
	DAC_MASK_1 |= (1<<pin1)
for pin2 in DAC_PINS_2:
	DAC_MASK_2 |= (1<<pin2)

''' DAC_MASK_# is a bit mask of the GPIO pins which that DAC uses,
    expressed here in the form b7,...,b0. This is XOR'd with the
    gpioWrite_Bits_0_31_Set bit-mask (inverts for gpioWrite_Bits_0_31_Clear)
'''

# Nice to use for debugging
def pause(string = ""):
        if string != "":
                string += "\n"
        input(string+"Pause, press <ENTER> to continue...")


'''--------------------------------   SSH   --------------------------------'''
def Ssh_Start_Receiver(mask_length):
    print("Starting Receiver")
    
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
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


'''---------------------------   On-Off Keying   ---------------------------'''
def Get_Dummy_OOK_Data():
    '''data = np.unpackbits(np.loadtxt('OOK_DATA_INPUT_firstattempt.txt'))
    for i in data:
        i = int(i)'''
    data = []
    for i in range(1000):
        data.append(0)
        data.append(1)
    return data
    '''
    print("No transition")
    arr = ([1,0]*8)*1000

    print("Half transition")
    arr = ([1,0]*4+[0]*8)*1000
    
    print("Full transition")
    arr = ([1, 0]*4+[0, 1]*4)*1000
    '''
'''
    arr = [0]
#    for i in range(1,11):
#        for j in range(i):
#            arr.append(1)
#        arr.append(0)
    for i in range (1,11):
            arr.append(0)
            arr.append(0)

    arr *= 10000
'''
    

def Get_Binary_Image():
    ''' TO BE ADDED '''
        


def Transmit_Binary_Data(data_list):
    import RPi.GPIO as GPIO
    
    try:
        # Use BCM numbering standard
        GPIO.setmode(GPIO.BCM);
        CLK_PIN = 20
        DATA_PIN = 21
        # Set BCM pin 4 as an output
        GPIO.setup(DATA_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(CLK_PIN, GPIO.OUT, initial=GPIO.LOW)

        half_clock = 1 / (2 * OOK_TRANS_FREQ)
        
        print("Transmitting data")

        if TRANSMISSION_TYPE == "FSK":
            for b in data_list:
                GPIO.output(DATA_PIN, b)
                GPIO.output(CLK_PIN, GPIO.HIGH)            
                sleep(half_clock*(b+1))
                GPIO.output(CLK_PIN, GPIO.LOW)
                sleep(half_clock*(b+1))
            GPIO.output(DATA_PIN, GPIO.LOW)
        else:
            for b in data_list:
                GPIO.output(DATA_PIN, b)
                GPIO.output(CLK_PIN, GPIO.HIGH)            
                sleep(half_clock)
                GPIO.output(CLK_PIN, GPIO.LOW)
                sleep(half_clock)
            GPIO.output(DATA_PIN, GPIO.LOW)
        print("Data transmission complete!")
        
    except KeyboardInterrupt:
        print("\nExiting program on keyboard interrupt")
    except Exception as e:
        print("\nExiting program on unexpected error\nError is: {}".format(e))
    finally:
        print("Cleaning up GPIOs")
        GPIO.cleanup()


'''---------------------- Advanced Modulation Schemes ----------------------'''
def Get_Step_Bytes():
    # This outputs steps so you can check DAC works

    # SYMB_RATE = 1 - 256PAM
    step = np.arange(4,dtype='uint8')*85
    multiple = np.tile(step, 10)

    #SYMB_RATE = 25 - 256PAM
    step_fine = np.arange(256,dtype='uint8')
    multiple_fine = np.tile(step_fine, 2)

    # SYMB_RATE = 4 - 4PAM (27 is 0b00011011 ie a ramp)
    pam4_once = np.ones(1, dtype='uint8')*27
    pam4 = np.ones(25, dtype='uint8')*27
    pam4 = np.tile(pam4,1000)

    return pam4

def Get_4PAM_Step_Bytes():
    once = np.array([0,1,2,3],dtype='uint8')
    multiple = np.tile(once, 10000) 
    return multiple
                

def Get_Image_Bytes(path):
    # PIL modes - RGB, L (greyscale)
    if "bw" in path:
        img = io.imread(path)
    else:
        img = io.imread(path, pilmode = 'RGB')
        
    size = img.size

    return img.reshape(size)


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

    # DAC Lookup table because DAC output is not working properly
    DAC_lookup = [0, 74, 170, 252]

    if TRANSMISSION_TYPE == "256PAM":
        # 1 SYMB/byte --> 0, 1, ..., 255
        # DAC = INPUT
        # MASK
        mask = np.zeros(data_list.size, dtype='uint32')
        for i, DAC_level in enumerate(data_list):
            if i % 25000 == 0 and i != 0:  #Stats
                print("Symbol - {}".format(i))
            mask32 = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & DAC_level:
                    mask32 |= (1<<pin)
            mask[i] = mask32
        print("Num of masks: {}".format(mask.size))
        return mask

    elif TRANSMISSION_TYPE == "4PAM":
        # 4 SYMB/byte --> 0, 1, 2, 3
        mapping_table = {(0,0) : 0,
                         (0,1) : 1,
                         (1,0) : 2,
                         (1,1) : 3}
        def Mapping(bits):
            return np.array([mapping_table[tuple(b)] for b in bits])

        
        data_list_bits = np.unpackbits(data_list)\
                         .reshape((np.unpackbits(data_list).size//2,2))
        symb = Mapping(data_list_bits)
        
        '''
        OLD METHOD
        symb = np.zeros(4*data_list.size, dtype='uint32')
        for i, byte in enumerate(data_list):
            if i % 25000 == 0 and i != 0:  #Stats
                    print("List val - {}".format(i))
            for s in range(4):
                symb[4*i+3-s] = ((1<<(2*s+1) | 1<<(2*s)) & byte) \
                                                   // (2**(2*s))
        '''
        # DAC
        # IF DAC WERE WORKING USE THIS INSTEAD OF LOOKUP
        #symb *= 85  # dac = symb * 85 --> 0, 85, 170, 255
        symb = np.array([DAC_lookup[s] for s in symb])
        #print(symb)
        # MASK
        mask = np.zeros_like(symb)
        for i, DAC_level in enumerate(symb):
            if i % 100000 == 0:  #Stats
                print("Mask - {}".format(i))
            mask32 = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & DAC_level:
                    mask32 |= (1<<pin)
            mask[i] = mask32
        print("Num of masks: {}".format(mask.size))
        return mask
    elif TRANSMISSION_TYPE == "16QAM":
        # 2 SYMB/byte --> I = 0, 1, 2, 3 : Q = 0, 1, 2, 3 SYMB is I,Q
        # Expressing I as col 1, Q as col 2 of N x 2 matrix
        mapping_table = {
            (0,0,0,0) : 0 + 0j,
            (0,0,0,1) : 0 + 1j,
            (0,0,1,0) : 0 + 3j,
            (0,0,1,1) : 0 + 2j,
            (0,1,0,0) : 1 + 0j,
            (0,1,0,1) : 1 + 1j,
            (0,1,1,0) : 1 + 3j,
            (0,1,1,1) : 1 + 2j,
            (1,0,0,0) : 3 + 0j,
            (1,0,0,1) : 3 + 1j,
            (1,0,1,0) : 3 + 3j,
            (1,0,1,1) : 3 + 2j,
            (1,1,0,0) : 2 + 0j,
            (1,1,0,1) : 2 + 1j,
            (1,1,1,0) : 2 + 3j,
            (1,1,1,1) : 2 + 2j
            }
        def Mapping(bits):
            return np.array([mapping_table[tuple(b)] for b in bits])

        
        data_list_bits = np.unpackbits(data_list)\
                         .reshape((np.unpackbits(data_list).size//4,4))
        symb = Mapping(data_list_bits)
                
        '''
        OLD METHOD
        symb = np.zeros((2*data_list.size, 2), dtype=np.uint32)
        # Each value pair (indexed 0 to 15) gives I, Q for that
        # 4-bit value (grey coded)
        qam_const = np.array([[2,2],[3,2],[2,3],[3,3],\
                              [2,1],[2,0],[3,1],[3,0],\
                              [1,2],[1,3],[0,2],[0,3],\
                              [1,1],[0,1],[1,0],[0,0]])

        for i, byte in enumerate(data_list):
            if i % 25000 == 0 and i != 0:  #Stats
                    print("Symbol - {}".format(2*i))
            symb[2*i] = qam_const[byte // 16]
            symb[2*i+1] = qam_const[byte % 16]
            '''
        # DAC
        # IF DAC WERE WORKING USE THIS INSTEAD OF LOOKUP
        # symb *= 85  # dac = symb * 85 --> 0, 85, 170, 255
        symb = np.array([DAC_lookup[int(s.real)] for s in symb]) \
               + np.multiply(np.array([DAC_lookup[int(s.imag)] for s in symb]),1j)
        # MASK
        mask = np.zeros(symb.size, dtype=np.uint32)
        for i, DAC_levels in enumerate(symb):
            if i % 25000 == 0 and i != 0:  #Stats
                print("Mask - {}".format(i))
            mask32 = 0
            # Assign real level to I DAC and imag level to Q DAC
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & int(DAC_levels.real):
                    mask32 |= (1<<pin)
            for j, pin in enumerate(DAC_PINS_2):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & int(DAC_levels.imag):
                    mask32 |= (1<<pin)
            mask[i] = mask32
        print("Num of masks: {}".format(mask.size))
        return mask
    else:
        print("Transmission type not implemented yet!")


def Invert_Mask(masks):
    if "PAM" in TRANSMISSION_TYPE:
        return masks ^ DAC_MASK_1
    else:
        return masks ^ (DAC_MASK_1 | DAC_MASK_2)


def Save_To_File(mask, path):
    mask.astype('uint32').tofile(path)


def Transmit_Data():
    print("Transmitting data...\nEstimated {}min, {}sec transmit time..."\
          .format(SIZE//(60*SYMB_RATE),round(100*60*((SIZE/(60*SYMB_RATE))%1))/100))
    
    transmitter = run(["sudo","./PiTransmit_3",str(SYMB_RATE)], stdout=PIPE, stderr=PIPE)
    print("\n... C TRANSMITTER LOGS ...\n")
    for line in transmitter.stdout.decode('utf-8').split('\n'):
        if line != "":
            print("... {}".format(line))
    for line in transmitter.stderr.decode('utf-8').split('\n'):
        if line != "":
            print("... ERR... {}\n".format(line))
    return_code = transmitter.returncode

    return_options = {0: "Data transmission complete!",
                      1: "Data transmission failed!",
                      2: "GPIO INIT FAIL",         # TODO: Add more failure codes?
                      3: "PiTransmit_3 ... Incorrect usage\n\nUsage: sudo ./PiTransmit_3 SYMB_RATE\n",
                      4: "Mask file and Invert mask file different lengths."}

    if return_code in return_options:
        print(return_options[return_code])
    else:
        print("Unrecognised return code: {}".format(return_code))


'''---------------------   Check Input Masks Correct   ---------------------'''
def Check_Input_Masks(input_vals, mask, mask_inv):
    '''
    Use this with RPiSim.GPIO in Windows to make sure mask for each number
    is what you expect in terms of the pins it changes - don't do for too
    many itterations just to check values
    '''
    print("Starting MASK test")
    from RPiSim.GPIO import GPIO
    GPIO.setmode(GPIO.BCM)
    if "PAM" in TRANSMISSION_TYPE:
        for pin in DAC_PINS_1:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    elif "QAM" in TRANSMISSION_TYPE:
        for pin in DAC_PINS_1 + DAC_PINS_2:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            
    if TRANSMISSION_TYPE == "256PAM":
        for i, m in enumerate(mask):
            # This is slow but exhaustively checks all possibilities
            for pin in DAC_PINS_1:
                if 1<<pin & m:
                    GPIO.output(pin, GPIO.HIGH)
                if 1<<pin & mask_inv[i]:
                    GPIO.output(pin, GPIO.LOW)
            pause("Input value {} = {}, mask displayed"\
                  .format(input_vals[i], bin(input_vals[i])))
            
    elif TRANSMISSION_TYPE == "4PAM":
        for i, inp in enumerate(input_vals):
            for j in range(4):
                # This is slow but exhaustively checks all possibilities
                for pin in DAC_PINS_1:
                    if 1<<pin & mask[4*i+j]:
                        GPIO.output(pin, GPIO.HIGH)
                    if 1<<pin & mask_inv[4*i+j]:
                        GPIO.output(pin, GPIO.LOW)
                pause("Input value {} = {}, mask {}/4 displayed"\
                      .format(inp, bin(inp), j+1))
                
    elif TRANSMISSION_TYPE == "16QAM":
        qam_const = np.array([[2,2],[3,2],[2,3],[3,3],\
                              [2,1],[2,0],[3,1],[3,0],\
                              [1,2],[1,3],[0,2],[0,3],\
                              [1,1],[0,1],[1,0],[0,0]])
        for i, inp in enumerate(input_vals):
            for j in range(2):
                # This is slow but exhaustively checks all possibilities
                for pin in DAC_PINS_1 + DAC_PINS_2:
                    if 1<<pin & mask[2*i+j]:
                        GPIO.output(pin, GPIO.HIGH)
                    if 1<<pin & mask_inv[2*i+j]:
                        GPIO.output(pin, GPIO.LOW)
                if inp < 16:
                    print("Second mask should be: [{}]")
                pause("Input value {} = {}, mask {}/2 displayed\n{}, {}"\
                      .format(inp, bin(inp), j+1, \
                              qam_const[inp//16], qam_const[inp%16]))
        
    else:
        pause("Test doesn't exist yet for other modulation schemes")                


'''--------------------------------   Main   --------------------------------'''
def main():
    #pause("Start")
        
    if TRANSMISSION_TYPE == "OOK":
        # Data stored as bits in Python lists
        # Transmitted using RPi.GPIO Python library
        
        input_stream = Get_Dummy_OOK_Data()
        #input_stream = Get_Binary_Image()
        
        # TODO: Encode_Error_Correction(input_stream)
        
        receiver_started = Ssh_Start_Receiver(len(input_stream))
        if receiver_started:
            print("About to transmit...")
            # Four seconds enough time to start receiver but not timeout
            sleep(4)
            Transmit_Binary_Data(input_stream)
            # TODO: Fetch_Receiver_Logs()
        else:
            print("Receiver never started")
        
    elif TRANSMISSION_TYPE == "basic_FSK":
        data = Get_Dummy_OOK_Data()
        input_stream = []
        for bit in data:
            if bit == 1:
                input_stream.append(1)
                input_stream.append(0)
            else:
                input_stream.append(1)
                input_stream.append(1)
                input_stream.append(0)
                input_stream.append(0)
        receiver_started = Ssh_Start_Receiver(len(input_stream))
        if receiver_started:
            print("About to transmit...")
            # Four seconds enough time to start receiver but not timeout
            sleep(4)
            Transmit_Binary_Data(input_stream)
            # TODO: Fetch_Receiver_Logs()
        else:
            print("Receiver never started")

    else:
        # Data stored as bytes/masks in NumPy arrays
        # Transmitted using compiled C code
        
        input_stream = Get_Step_Bytes()
        #input_stream = Get_Image_Bytes('cat2_bw.jpg')
        #input_stream = Get_4PAM_Step_Bytes()
        print("Input stream length (bytes): {}".format(input_stream.size))

        print("Converting data to masks...")
        input_mask = Convert_To_Data_Mask(input_stream)
        input_mask_inv = Invert_Mask(input_mask)
        print("Saving data as masks...")
        Save_To_File(input_mask, DATA_PATH)
        Save_To_File(input_mask_inv, DATA_INV_PATH)
        
        global SIZE
        SIZE = input_mask.size

        # In Windows to check masks are being generated correctly for pins
        # Check_Input_Masks(input_stream, input_mask, input_mask_inv)
        #pause("About to transmit...")
        receiver_started = Ssh_Start_Receiver(SIZE)
        if receiver_started:
            print("About to transmit...")
            # Five seconds enough time to start receiver but not timeout
            sleep(5)
            Transmit_Data()
            # TODO: Fetch_Receiver_Logs()
        else:
            print("Receiver never started")

    
    print("\nFinishing program")


# Use try when debugging to catch errors, not necessary for use
try:
    main()
except KeyboardInterrupt:
    print("\nExiting program on keyboard interrupt")
except Exception as e:
    print("\nExiting program on unexpected error\n\tError is: {}".format(e))
