from time import time

def time_For():
    t0=time()
    for i in range(0,1000):
        pass
    t1=time()-t0
    print("Time of For loop: {}".format(t1/1000))
    
def time_While():
    i = 0
    t0=time()
    while(1):
        if i>1000:
            break
        else:
            i = i+1
    t1=time()-t0
    print("Time of While loop: {}".format(t1/1000))	

time_For()
time_While()
