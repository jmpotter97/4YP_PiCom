LOGS = ["********** RECEIVER LOG FILE **********\n\n"]
output = []
transmission_type = "4PAM"

def Receive_Data(LOGS):
    LOGS.append("Receiving data\n")
    
    if transmission_type == "4PAM":
        return_code = call(["sudo","./PiReceive"])
    elif transmission_type == "4QAM":
        LOGS.append("4QAM NO EXIST")
        # Doesn't exist yet
        # return_code = call(["./PiReceive_2_QAM", "arg1", "arg2", "arg3"])
    else:
        return_code = -1

    if not return_code:
        LOGS.append("Data receive complete!\n")
        with open('OUT.txt', 'r') as f:
            output = f.read()
    else:
        if return_code == -1:
            LOGS.append("Invalid transmission type!\n")
        elif return_code == 1:
            LOGS.append("Data receive failed!\n") # Add more failure codes
        elif return_code == 2:
            LOGS.append("GPIO INIT FAIL")
        else:
            pass

    return output
    


def Decode_Error_Correction(output):
    ''' TO BE ADDED '''


if __name__ == '__main__':
    try:
        output = Receive_Data(LOGS)
        if len(output) == 0:
            LOGS.append("No data was received\n")
        else:
            '''
            Decode_Error_Correction(output)
            '''
            LOGS.append("Saving output to file\n")
            with open('OUTPUT.txt', 'w') as f:
                f.write("".join(str(i) for i in output))
            '''
            Save_As_Image(output) ### TO DO WHEN POSSIBLE, REMOVE PREVIOUS SAVE TO FILE
            '''
        else:
            LOGS.append("Receiver timeout waiting for signal\n")


    except KeyboardInterrupt:
        LOGS.append("\nExiting on keyboard interrupt!\n")
    except Exception as e:
        LOGS.append("\nExiting on unexpected error!\nError is: {}".format(e))

    finally:
        with open('LOGS.txt', 'w') as f:
            for l in LOGS:
                f.write(l)
