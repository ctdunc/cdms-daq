## script to find highest possible data_frequency/io_time ratio.
import os
import time
import nidaqmx as ni
from AnalogInputDAQ import AIDAQ

freq_cap = 8e5
freq_cutoff = 2e5

fre = freq_cap
tra = 100000

def rat(f, t):
	a = AIDAQ(sr=f,trlen=t,savefile="test.h5")
	num_f = 0
	try:
		starttime = time.time()
		a.init_config()
		a.start()
		input("tet")
		size = a.size
		a.close()
		print('hi i am exec this code')
		endtime=time.time()
		print(size/(endtime-starttime))
	except ni.errors.DaqError:
		num_f += 1


	
rat(fre,tra)

