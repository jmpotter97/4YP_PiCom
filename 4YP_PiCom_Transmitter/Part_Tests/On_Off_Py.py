from time import time
import RPi.GPIO as G

def timer():
	t0=time()
	for i in range(0,1000):
		G.output(6,G.HIGH)
		G.output(6,G.LOW)
	t1=time()-t0
	print("Time per operation")
	print(t1/2000)
	print("Frequency")
	print(2000/t1)

G.setmode(G.BCM)
G.setup(6,G.OUT)
timer()
G.cleanup()
