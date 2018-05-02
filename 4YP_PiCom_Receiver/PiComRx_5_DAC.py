import numpy as np
import imageio as io
from time import sleep
from subprocess import run, PIPE
from sys import argv
import os

LOGS_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/LOGS.txt"
if os.path.isfile(LOGS_PATH):
    os.remove(LOGS_PATH)
LOGS = ["********** RECEIVER LOG FILE **********\n"]
DATA_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/data_masks.bin"
TRANSMISSION_TYPES = ["OOK", "256PAM", "4PAM", "16QAM"] #, "OFDM"] to be added
TRANSMISSION_TYPE = "4PAM"

if len(argv) > 2:
    TRANSMISSION_TYPE = argv[2]

if TRANSMISSION_TYPE not in TRANSMISSION_TYPES:
    LOGS.append("\nINVALID TRANSMISSION TYPE, EXITING\n")
    LOGS.append("***************************************\n")
    with open(LOGS_PATH, 'w') as f:
        for l in LOGS:
            f.write(l)
            # Print to output while working on receiver file
            print(l, end='')
    import sys
    sys.exit(1)
else:
    LOGS.append("TRANSMISSION TYPE: {}\n".format(TRANSMISSION_TYPE))

DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [14, 15, 18, 17, 27, 22, 23, 24]


# Nice to use for debugging
def pause(string = ""):
        if string != "":
                string += "\n"
        input(string+"Pause, press <ENTER> to continue...")


'''---------------------------   On-Off Keying   ---------------------------'''
def Receive_Binary_Data(out, LOGS):
    import RPi.GPIO as GPIO

    try:
        # Use BCM numbering standard
        GPIO.setmode(GPIO.BCM)
        CLK_PIN = 20
        DATA_PIN = 21
        # Setup input and clock pins as IN-puts with pull-down (PUD_DOWN) resistor
        GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        still_receiving = True

        if GPIO.wait_for_edge(CLK_PIN, GPIO.RISING, timeout=10000) is not None:
            out.append(GPIO.input(DATA_PIN))
            while still_receiving:
                if GPIO.wait_for_edge(CLK_PIN, GPIO.RISING, timeout=1000) is not None:
                       out.append(GPIO.input(DATA_PIN))
                else:
                    still_receiving = False
        else:
            LOGS.append("Receiver timeout waiting for signal to start\n")
    except KeyboardInterrupt:
        LOGS.append("\nExiting program on keyboard interrupt\n")
    except Exception as e:
        LOGS.append("\nExiting program on unexpected error\nError is: {}\n".format(e))
    finally:
        LOGS.append("Cleaning up GPIOs\n")
        GPIO.cleanup()


'''---------------------- Advanced Modulation Schemes ----------------------'''
def Receive_Data(size, LOGS):
    LOGS.append("Receiving data\n")
    receiver = run(["sudo", "./PiReceive", str(size)], stdout=PIPE)

    LOGS.append("\n... C RECEIVER LOGS ...\n\n")
    for line in receiver.stdout.decode('utf-8').split('\n'):
        LOGS.append("... {}\n".format(line))
    return_code = receiver.returncode
		
    return_options = { 0 : "Data transmission complete!\n",
		       1 : "Data receive failed! General error\n",
		       2 : "GPIO INIT FAIL\n",
                       3 : "\n--- PiReceive ---\nUsage: sudo ./PiReceive mask_size \n",
                       4 : "Memory to receive data was not allocated!",
                       5 : "Invalid Mask Size (Zero or not a number)"}

    if return_code in return_options:
        LOGS.append("\nReturn code: [{}] {}".format(return_code,return_options[return_code]))
        if not return_code:
            return np.fromfile(DATA_PATH, dtype='uint32')
        else:
            return np.empty(0)
    else:
        LOGS.append("Invalid return code: [{}]".format(return_code))
        return np.empty(0)


def Decode_Masks(masks, LOGS):
    LOGS.append("Decoding masks...\n")

    '''
    MASK goes through a number of stages:
    DAC  - FOR EACH PIN ON THE DAC, INCLUDE IF IN THE MASK
            I AND Q DAC FOR QAM
    SYMB - CHECK ATTENUATION (MAX), ADJUST, MAX LIKELIHOOD ESTIMATION
            TO REGAIN EACH SYMBOL VALUE
    OUT  - CHANGE EACH SET OF SYMBOL/LEVELS INTO OUTPUT BYTES
    '''

    
    if TRANSMISSION_TYPE == "256PAM":
        # This can't be adjusted for errors in the DAC so can only really be
        # tested if pins connected directly without the DAC and ADC between
        out = np.zeros(masks.size, dtype='uint8')
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            out[i] = val
        return out

    elif TRANSMISSION_TYPE == "4PAM":
        # Will use maximum likelihood reconstruction and account for attenuation
        out = np.zeros(masks.size//4, dtype='uint8')
        # DAC
        # Masks are 32-bit
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            masks[i] = val
        # Masks are 8-bit but attenuated
        highest = max(masks)
        LOGS.append("Attenuation = {}\n".format( (255-highest) / 255 ))
        # SYMB
        for i in range(masks.size):
            if highest != 255 and highest != 0:
                masks[i] = round(masks[i]*255/highest)
            # Masks are 8-bit and full-range
            # Maximum likelihood reconstruction of masks to symbols:
            if masks[i] < 0.5*85:
                masks[i] = 0
            elif 0.5*85 < masks[i] < 1.5*85:
                masks[i] = 1
            elif 1.5*85 < masks[i] < 2.5*85:
                masks[i] = 2
            else:
                masks[i] = 3
        # OUT
        for i in range(out.size):
            for s in range(4):
                out[i] |= (2 ** (2*s)) * masks[4*i+3-s]
        return out
    elif TRANSMISSION_TYPE == "16QAM":
        out = np.zeros((masks.size//2, 2), dtype='uint8')
        # SYMB
        symb = np.zeros((masks.size//2, 2), dtype='uint32')
        # DAC
        # Masks are 32-bit
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            masks[i] = val
        '''# 2 SYMB/byte --> I = 0, 1, 2, 3 : Q = 0, 1, 2, 3 SYMB is I,Q
        # Expressing I as col 1, Q as col 2 of N x 2 matrix
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
        # DAC
        symb *= 85  # dac = symb * 85 --> 0, 85, 170, 255
        # MASK
        mask = np.zeros(symb.shape[0], dtype=np.uint32)
        for i, DAC_levels in enumerate(symb):
            if i % 25000 == 0 and i != 0:  #Stats
                print("Mask - {}".format(2*i))
            mask32 = 0
            # Assign level[0] to I DAC and level[1] to Q DAC
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & DAC_levels[0]:
                    mask32 |= (1<<pin)
            for j, pin in enumerate(DAC_PINS_2):
                # If each bit in binary exists, include it in 32-bit mask
                if (1<<(7-j)) & DAC_levels[1]:
                    mask32 |= (1<<pin)
            mask[i] = mask32
        print("Num of masks: {}".format(mask.size))
        return mask'''
        out = np
        
    else:
        print("Transmission type not implemented yet!")


def Decode_Error_Correction(out, LOGS):
    ''' TO BE ADDED '''


def Save_As_Image(out, path, LOGS):
    if os.path.isfile(path):
        os.remove(path)
    if out.size == 256*256*3:
        io.imwrite(path, out.reshape(256,256,3))
    elif out.size < 256*256*3:
        img = np.zeros(256*256*3, dtype='uint8')
        for i, o in enumerate(out):
            img[i] = o
        io.imwrite(path, img.reshape(256,256,3))
    else:
        io.imwrite(path, out[:256*256*3].reshape(256,256,3))


'''--------------------------------   Main   --------------------------------'''
def main():
    pause("Start")
    if len(argv) > 1:
        mask_size = int(argv[1])

        if TRANSMISSION_TYPE == "OOK":
            output = []
            Receive_Binary_Data(output, LOGS)

            # TODO: Decode_Error_Correction(output)
            
            LOGS.append("Size of data: {}\nExpected size: {}\n".format(len(output), mask_size))
            with open('/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/OUTPUT.txt','w') as f:
                f.write("".join(str(i) for i in output))
        else:
            output_masks = Receive_Data(mask_size, LOGS)
            # For testing data_masks.bin file already received or created
            #output_masks = np.fromfile(DATA_PATH, dtype='uint32')
            
            if output_masks.size != 0:
                output = Decode_Masks(output_masks, LOGS)
                with open('/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/OUTPUT.txt','w') as f:
                    f.write("-".join(str(i) for i in output))
                #Save_As_Image(output, '/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/cat2_out.jpg', LOGS)
            else:
                LOGS.append("No data was received\n")
    else:
        LOGS.append("Mask size command line variable not correctly used\n")
        LOGS.append("\n------- PiComRx_5_DAC.py -------\n\nUsage: sudo python3 PiComRx_5_DAC mask_size [transmission_type]\n")


# Try necessary to save LOGS if error occurs in code,
# won't slow down C part of receiver
try:
    main()
    LOGS.append("\nCompleted Receiver code!\n")
except KeyboardInterrupt:
    LOGS.append("\nExiting on keyboard interrupt!\n")
except Exception as e:
    LOGS.append("\nExiting on unexpected error!\nError is: {}\n".format(e))
finally:
    LOGS.append("***************************************\n")
    with open(LOGS_PATH, 'w') as f:
        for l in LOGS:
            f.write(l)
            # Print to output while working on receiver file
            print(l, end='')
