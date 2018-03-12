from subprocess import call
LOGS = ["********** RECEIVER LOG FILE **********\n\n"]
transmission_type = "4PAM"


def pause():
	prPause = input("Pause, press <ENTER> to continue...")


def Receive_Data(out, LOGS):
    LOGS.append("Receiving data\n")
    
    if transmission_type == "4PAM":
        return_code = call(["sudo", "./PiReceive","5"])
    elif transmission_type == "4QAM":
        LOGS.append("4QAM NO EXIST")
        # Doesn't exist yet
        # return_code = call(["./PiReceive_2_QAM", "arg1", "arg2", "arg3"])
        return_code = -1
    else:
        return_code = -1

    if not return_code:
        LOGS.append("Data receive complete!\n")
        with open('OUT.txt', 'r') as f:
            for data in f.read().split(','):
                out.append(data)
    else:
        if return_code == -1:
            LOGS.append("Invalid transmission type!\n")
        elif return_code == 1:
            LOGS.append("Data receive failed!\n")
            # TODO: Add more failure codes
        elif return_code == 2:
            LOGS.append("GPIO INIT FAIL")
        elif return_code == 3:
            LOGS.append("\n--- PiReceive ---\n")
            LOGS.append("Usage: sudo ./PiReceive mask_size \n")
    for i in out:
        print(i)

def Decode_Error_Correction(output, LOGS):
    ''' TO BE ADDED '''


def Save_As_Image(output, LOGS):
    ''' TO BE ADDED '''


try:
    output = []
    Receive_Data(output, LOGS)
    for i in output:
        print(i)
    if len(output) == 0:
        LOGS.append("No data was received\n")
    else:
        '''
        Decode_Error_Correction(output)
        '''
        
        LOGS.append("Saving output to file\n")
        with open('OUTPUT.txt', 'w') as f:
            f.write(",".join(str(i) for i in output))
        # TODO: WHEN POSSIBLE, REMOVE PREVIOUS SAVE TO FILE
        '''
        Save_As_Image(output)
        '''

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
