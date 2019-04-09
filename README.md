# 4YP_PiCom

Fourth Year Project, Communications Testbed Between Two Rasberry Pi's

The idea of the project is to recreate the functionality of Software Defined Radio Testbeds using low-cost equipment and two Raspberry Pis. The final goal of the project is to have a communication testbed implementing various modulation schemes including On-Off Keying, Pulse Amplitude Modulation, and Quadrature Amplitude Modulation as well as attempting Orthogonal Frequency Division Multiplexing if possible.

The data manipulation is done in Python, and the actual control of the GPIO Pins is done using C, as pin value transition and code execution speeds are much higher. The main Receiver and Transmitter files are PiComRx_5_DAC.py and PiComTx_5_DAC.py (and the executables PiTransmit_3 and PiReceive based on C code of the .c files with the same names).

The project can be implemented by running the command "git clone https://github.com/jmpotter97/4YP_PiCom.git" to download all of the relevant files on each of two Raspberry Pis, and then setting up the hardware and naming the Raspberry Pis (or altering the code) as directed in the report (also in the git folder). The final reports can be found in the 'Reports' folder.

# J. Potter, based on work by C. Eadie