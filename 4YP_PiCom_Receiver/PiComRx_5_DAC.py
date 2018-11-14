import numpy as np
import imageio as io
from time import sleep
from subprocess import run, PIPE
from sys import argv
import os
import datetime

# {} in paths designed for .format(TransType+DATE_TIME)
DATA_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/data_masks.bin"
OUT_PATH  = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/OUTPUT_{}.txt"
LOGS_PATH = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/LOGS_{}.txt"
IMG_PATH  = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/cat2_out_{}.jpg"

if os.path.isfile(LOGS_PATH):
    os.remove(LOGS_PATH)
LOGS = ["********** RECEIVER LOG FILE **********\n"]

TRANSMISSION_TYPES = ["OOK", "256PAM", "4PAM", "16QAM"] #, "OFDM"] to be added
TRANSMISSION_TYPE = "4PAM"

if len(argv) > 2:
    TRANSMISSION_TYPE = argv[2]

if TRANSMISSION_TYPE not in TRANSMISSION_TYPES:
    LOGS.append("\nINVALID TRANSMISSION TYPE, EXITING\n")
    LOGS.append("***************************************\n")
    LOGS_PATH = LOGS_PATH.format(TRANSMISSION_TYPE+"_"+datetime.datetime.now().strftime("%H-%M"))
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
def Average(values):
    total = 0
    for value in values:
        total = total + value
    total = total/len(values)
    return total

def Receive_Binary_Data(out, LOGS, mask_size):
    import RPi.GPIO as GPIO
    overclocking = 1
    
    try:
        # Use BCM numbering standard
        GPIO.setmode(GPIO.BCM)
        CLK_PIN = 20
        DATA_PIN = 21
        # Setup input and clock pins as IN-puts with pull-down (PUD_DOWN) resistor
        GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        still_receiving = True
        count = 0
        length_counter = 0
        GPIO.wait_for_edge(DATA_PIN, GPIO.RISING, timeout=10000)
        out.append(GPIO.input(DATA_PIN))
        while still_receiving:
            GPIO.wait_for_edge(CLK_PIN, GPIO.FALLING, timeout=1000)
            value = GPIO.input(DATA_PIN)
            length_counter += 1
            if length_counter == mask_size:
                still_receiving = False
            else:
                count += 1
                if count == overclocking:
                    count = 0
                    out.append(value)
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
    C_receive_command = "/home/pi/Documents/4YP_PiCom/4YP_PiCom_Receiver/PiReceive"
    receiver = run(["sudo", C_receive_command, str(size)], stdout=PIPE, stderr=PIPE)

    LOGS.append("\n... C RECEIVER LOGS ...\n\n")
    for line in receiver.stdout.decode('utf-8').split('\n'):
        if line != "":
            LOGS.append("... {}\n".format(line))
    for line in receiver.stderr.decode('utf-8').split('\n'):
        if line != "":
            LOGS.append("... ERR... {}\n".format(line))
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
        lowest = min(masks)
        LOGS.append("Attenuation = {}\n".format( (255-(highest-lowest)) / 255 ))
        # SYMB
        for i in range(masks.size):
            if highest != 255 and highest != lowest and highest != 0:
                masks[i] = round((masks[i]-lowest)*255/(highest-lowest))
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
        out = np.zeros(masks.size//2, dtype='uint8')
        # DAC
        # Masks are 32-bit
        dac = np.zeros(masks.size, dtype='complex')
        for i, mask in enumerate(masks):
            val = 0
            for j, pin in enumerate(DAC_PINS_1):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            dac[i] = val
            val=0
            for j, pin in enumerate(DAC_PINS_2):
                # If each bit in mask exists, include it in out
                if (1<<pin) & mask:
                    val |= (1<<(7-j))
            dac[i] += val * 1j
        # DAC values are 8-bit but attenuated
        highest = int(max(np.hstack((dac.real,dac.imag))))
        lowest = int(min(np.hstack((dac.real,dac.imag))))
        LOGS.append("Attenuation = {}\n"\
                    .format( (255-(highest-lowest)) / 255 ))
        # SYMB
        for i in range(dac.size):
            re = dac[i].real
            im = dac[i].imag
            if highest != 255 and highest != lowest and highest != 0:
                dac[i] = round((re-lowest)*255/(highest-lowest))\
                         + round((im-lowest)*255/(highest-lowest))*1j
            # Masks are 8-bit and full-range
            # Maximum likelihood reconstruction of masks to symbols:
            if re < 0.5*85:
                dac[i] = 0
            elif 0.5*85 < re < 1.5*85:
                dac[i] = 1
            elif 1.5*85 < re < 2.5*85:
                dac[i] = 2
            else:
                dac[i] = 3
                
            if im < 0.5*85:
                dac[i] += 0j
            elif 0.5*85 < im < 1.5*85:
                dac[i] += 1j
            elif 1.5*85 < im < 2.5*85:
                dac[i] += 2j
            else:
                dac[i] += 3j

        mapping_table = {
            (0,0,0,0) : 0+0j,
            (0,0,0,1) : 0+1j,
            (0,0,1,0) : 0+3j,
            (0,0,1,1) : 0+2j,
            (0,1,0,0) : 1+0j,
            (0,1,0,1) : 1+1j,
            (0,1,1,0) : 1+3j,
            (0,1,1,1) : 1+2j,
            (1,0,0,0) : 3+0j,
            (1,0,0,1) : 3+1j,
            (1,0,1,0) : 3+3j,
            (1,0,1,1) : 3+2j,
            (1,1,0,0) : 2+0j,
            (1,1,0,1) : 2+1j,
            (1,1,1,0) : 2+3j,
            (1,1,1,1) : 2+2j
            }
        demap_table = { v : k for k, v in mapping_table.items() }
        
        def DeMapping(symbs):
            return np.array([demap_table[s] for s in symbs])
        
        output_bits = DeMapping(dac)
        out = np.packbits(output_bits)
        return out
    else:
        LOGS.append("Transmission type not implemented yet!")


def Decode_Error_Correction(out, LOGS):
    ''' TO BE ADDED '''


def EndZeros(array):
    i = 0
    j = 0
    while j == 0 and i<array.size:
        if array[-1-i] == 0:
            i = i+1
        else:
            j = 1
    return i

def Save_As_Image(out, path, LOGS):
    LOGS.append("End zeros: {} out of {}".format(EndZeros(out),256*256))
    if os.path.isfile(path):
        os.remove(path)
    if out.size == 256*256:
        io.imwrite(path, out.reshape(256,256))
    elif out.size < 256*256:
        img = np.zeros(256*256, dtype='uint8')
        for i, o in enumerate(out):
            img[i] = o
        io.imwrite(path, img.reshape(256,256))
    else:
        io.imwrite(path, out[:256*256].reshape(256,256))


'''--------------------------------   Main   --------------------------------'''
def main():
    #pause("Start")
    if len(argv) > 1:
        mask_size = int(argv[1])

        if TRANSMISSION_TYPE == "OOK":
            output = []
            Receive_Binary_Data(output, LOGS, mask_size)

            # TODO: Decode_Error_Correction(output)
            
            LOGS.append("Size of data: {}\nExpected size: {}\n".format(len(output), mask_size))
            global OUT_PATH
            OUT_PATH = OUT_PATH.format(TRANSMISSION_TYPE+"_"+datetime.datetime.now().strftime("%H-%M"))
            with open(OUT_PATH,'w') as f:
                f.write("".join(str(i) for i in output))
        else:
            output_masks = Receive_Data(mask_size, LOGS)
            # For testing data_masks.bin file already received or created
            #output_masks = np.fromfile(DATA_PATH, dtype='uint32')
            
            if output_masks.size != 0:
                output = Decode_Masks(output_masks, LOGS)
                '''with open(OUT_PATH,'w') as f:
                    f.write("-".join(str(i) for i in output))'''
                global IMG_PATH
                IMG_PATH = IMG_PATH.format(TRANSMISSION_TYPE+"_"+datetime.datetime.now().strftime("%H-%M"))
                Save_As_Image(output, IMG_PATH, LOGS)
            else:
                LOGS.append("No data was received\n")
    else:
        LOGS.append("Mask size command line variable not correctly used\n")
        LOGS.append("\n------- PiComRx_5_DAC.py -------\nMask size not provided\n\nUsage: sudo python3 PiComRx_5_DAC mask_size [transmission_type]\n")


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
    global LOGS_PATH
    LOGS_PATH = LOGS_PATH.format(TRANSMISSION_TYPE+"_"+datetime.datetime.now().strftime("%H-%M"))
    with open(LOGS_PATH, 'w') as f:
        for l in LOGS:
            f.write(l)
            # Print to output while working on receiver file
            print(l, end='')
