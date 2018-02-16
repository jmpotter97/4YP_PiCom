# Using paramiko SSH library
import paramiko

def ssh_start_receiver():
    host = "raspberrypi2.local"
    uname = "pi"
    pword = "rasPass2"
    command = "sudo python3 /home/pi/Documents/sshConfirm.py"
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
        print("Unknown error in ssh connection")

    if ssh.get_transport().is_active():
        print("Executing command to start Receiver")
        stdin, stdout, stderr = ssh.exec_command(command)
        print("Started...")
        while not stdout.channel.exit_status_ready():
            for line in iter(stdout.readline, ""):
                print("... "+line, end="")
                if line == "SUCCESS":
                    print("Closing successful ssh connection\n")
                    ssh.close()
                    return 1
        ssh.close()
        print("Success overshoot")
        return 0
        
    else:
        print("Closing unsuccessful ssh connection\n")
        ssh.close()
        return 0

if ssh_start_receiver():
    print("\nWell done!!!")
else:
    print("\nOh no!!!")

