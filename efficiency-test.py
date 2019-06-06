## script to find highest possible data_frequency/io_time ratio.
import os
import time
import nidaqmx as ni
from AnalogInputDAQ import AIDAQ

def test():
    f = 6.25e5
    t = f/4
    a = AIDAQ(sr=f,trlen=t,savefile="test.h5")
    a.init_config()
    starttime=time.time()
    a.start()
    input('testing')
    a.close()
    endtime=time.time()
    tes = a.size/(endtime-starttime)
    print(tes)
    
    return 0

if __name__ == '__main__':
    test()
	
