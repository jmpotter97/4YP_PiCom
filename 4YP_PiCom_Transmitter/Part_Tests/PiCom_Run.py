from subprocess import call
return_code = call(["./PiTransmit", "arg1", "arg2", "arg3"])
if return_code == 0:
    print("Data transmission complete!")
elif return_code == 1:
    print("GPIO FAIL LOL")
