# 4YP_PiCom

## Fourth Year Project, Communications Testbed Between Two Rasberry Pi's

The idea of the project is to recreate the functionality of Software Defined Radio Testbeds using low-cost equipment and two Raspberry Pis. The final goal of the project is to have a communication testbed implementing various modulation schemes including On-Off Keying, Pulse Amplitude Modulation, and Quadrature Amplitude Modulation as well as attempting Orthogonal Frequency Division Multiplexing if possible.

The data manipulation is done in Python, and the actual control of the GPIO Pins is done using C as transition and code execution speeds are much higher. The main Receiver and Transmitter files are PiComRx_5_DAC.py and PiComTx_5_DAC.py.

The project can be implemented by running the command "git clone https://github.com/CamEadie/4YP_PiCom.git" to download all of the relevant files on two Raspberry Pis, and then setting up the hardware as directed in the report (also in the git folder under Report/main.pdf).
