import numpy as np
import imageio as io
from time import sleep
from subprocess import run, PIPE
from sys import argv
from os import remove

os.remove('LOGS.txt')
LOGS = ["********** RECEIVER LOG FILE **********\n\n"]
TRANSMISSION_TYPES = ["256PAM", "4PAM", "16QAM"] #, "OFDM"] to be added
TRANSMISSION_TYPE = "4PAM"
DATA_PATH = "data_masks.bin"

DAC_PINS_1, DAC_PINS_2 = [10, 9, 11, 5, 6, 13, 19, 26], \
                         [2, 3, 4, 17, 27, 22, 23, 24]


# Nice to use for debugging
def pause(string = ""):
        if string != "":
                string += "\n"
        input(string+"Pause, press <ENTER> to continue...")


def Receive_Data(size, LOGS):
    LOGS.append("Receiving data\n")

    if TRANSMISSION_TYPE in TRANSMISSION_TYPES:
        receiver = run(["sudo", "./PiReceive", str(size)], stdout=PIPE)
        
        for line in transmitter.stdout.decode('utf-8').split('\n'):
            LOGS.append("... {}".format(line))
        return_code = receiver.returncode
    else:
        return_code = -1
		
    return_options = {-1 : "Invalid transmission type!\n",
		       0 : "Data transmission complete!\n",
		       1 : "Data receive failed!\n",
		       2 : "GPIO INIT FAIL\n",	 # Add more failure codes
		       3 : "\n--- PiReceive ---\nUsage: sudo ./PiReceive mask_size \n"}
			
    if return_code in return_options:
	LOGS.append(return_options[return_code])
	if not return_code:
            return np.fromfile(DATA_PATH, dtype='uint32')
        else:
            return np.empty(0)
    else:
        LOGS.append("Invalid return code: {}".format(return_code))
        return np.empty(0)


def Decode_Masks(masks, LOGS):
    LOGS.append("Decoding masks...")
    if TRANSMISSION_TYPE == "256PAM":
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
        out = np.zeros(masks.size//4, dtype='float)
        for i, o in enumerate(out):
            for s in range(4):
                out[i] |= (2**(2*s)) * masks[4*i+3-s]
''' Need this before recombining 4 values!!!
        if max(out) == 255:
            LOGS.append("Attenuation = 0")
        else:
            att = max(out)
            LOGS.append("Attenuation = {}".format(att))
            out /= att
'''
        
        # MASK
        mask = np.zeros_like(symb)
        for i, DAC_level in enumerate(symb):
            if i % 25000 == 0 and i != 0:  #Stats
                print("Mask - {}".format(4*i))
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
        return mask
    else:
        print("Invalid transmission type!")


def Decode_Error_Correction(out, LOGS):
    ''' TO BE ADDED '''


def Save_As_Image(out, path, LOGS):
        if out.size == 160000:
            io.imwrite(path, out.reshape(400,400), pilmode = 'L')
        elif out.size < 160000
            img = np.ones(160000, dtype='uint8') * 255
            for i, o in enumerate(out):
                img[i] = o
            io.imwrite(path, img.reshape(400,400), pilmode = 'L')
        else:
            io.imwrite(path, out[:160000].reshape(400,400), pilmode = 'L')


try:
    if len[argv] == 2:
        mask_size = argv[1]
        output_masks = Receive_Data(mask_size, LOGS)

        if output_masks.size != 0:
            output = Decode_Masks(output_masks, LOGS)
            
            # TODO: Decode_Error_Correction(output)
            
            Save_As_Image(output, 'cat_out.png', LOGS)
        else:
            LOGS.append("No data was received\n")
    else:
        LOGS.append("\n--- PiComRx_5_DAC ---\nUsage: sudo python3 PiComRx_5_DAC mask_size\n")

except KeyboardInterrupt:
    LOGS.append("\nExiting on keyboard interrupt!\n")
except Exception as e:
    LOGS.append("\nExiting on unexpected error!\nError is: {}".format(e))

finally:
    with open('LOGS.txt', 'w') as f:
        for l in LOGS:
            f.write(l)

if __name__ == '__main__':
    with open('LOGS.txt', 'r') as f:
        print(f.read())
