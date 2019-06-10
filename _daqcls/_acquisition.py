import nidaqmx as ni
import h5py as hp
import numpy as np
import time


class __VDAQ(ni.Task):
    """
    HOC for Voltage Data AcQuisition objects with HDF5 save capabilities.
    -------------------
    Parameters:
    -------
    - device:   nidaqmx pointer to physical device. ex: 'Dev1/ai0'
    - savefile: hdf5 savefile. if no file is provided, data will not be saved.
    - group:    group within hdf5 savefile. default is '/'
    -------
    """
    def __init__(
            self, 
            device,
            savefile='', 
            group=''):

        ##############################  
        # HDF5 savefile configuration
        ##############################  

        if savefile:
            self.SAVE       =   True
            self.savefile   =   hp.File(savefile,'a') 
            if group:
                try:
                    self.group      =   self.savefile.create_group(group)
                except ValueError:
                    print('HDF5 group ' + group + ' already exists! Skipping creation')
            else:
                    self.group      =   self.savefile   # savefile object is also root group per h5py documentation.
        else:
            self.SAVE       =   False
            print('no savefile specified. data will be lost')

        ##############################  
        # NI task configuration
        ##############################
        ni.Task.__init__(self)                              # start NI task object
        self.device     =   device

        self.ai_channels.add_ai_voltage_chan(self.device)   # creates analog input voltage channel at specified device
        


class cVDAQ(__VDAQ):
        """
        continuous Volatage Data AcQuisition extends __VDAQ
        ---------
        Parameters:

        """
	def __init__(self, **kwargs):		
            __VDAQ.__init__(self)
		default = 	{
					'sr' : model.get(kwargs.get('model', ''), 1e5), 		  # prioritizes setting sample rate by max card setting
					'trlen' : kwargs.get('sr', model.get(kwargs.get('model',''),1e5)),# set trace length=sample rate by default
					'device' : 'Dev1/ai0',						  # you should almost certainly spec this
					'savefile' : 'test.h5',						  # and this
					'group' : 'traces',
					'dataset' : None
				}

		# sets all object keys according to priority as defined above
		for key in default.keys():
			setattr(self, key, kwargs.get(key, default[key]))
		self.dt	=	1/self.sr
		self.df =	self.trlen/self.sr
		
		self.sr = int(self.sr)
		self.trlen = int(self.trlen)

		self.savefile = hp.File(self.savefile, 'a')
		try:
			self.grp	=	self.savefile.create_group(self.group)
		except ValueError:
			print("group %s exists, skipping", self.group)
			self.grp	=	self.savefile[self.group]
		self.dst	=	self.grp.create_dataset(
						'ai_'+str(time.localtime()),
						(self.trlen,),
						chunks=(60*self.sr,),	# chunks in 1 minute interval
						maxshape=(None,)
						)


	# initializes config variables based on class parameters. 
	# Must be called before using AIDAQ.start() (extended from nidaqmx.Task.start())
	def init_config(self):
		self.ai_channels.add_ai_voltage_chan(self.device)

		self.timing.cfg_samp_clk_timing(
				self.sr,
				sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
				samps_per_chan=self.sr
				)

		self.register_every_n_samples_acquired_into_buffer_event(
				self.trlen,
				self.__every_n_cb)

		return 0

	def __every_n_cb(self, task_handle, every_n_samples_event_type,
			number_of_samples, callback_data):

		# read samples according to trace length
		samples = self.read(number_of_samples_per_channel=self.trlen)
		
		# save trace to hdf5
		self.__save_data(samples)
		

		return 0

	def __save_data(self, samples):
		# resize dataset to accept new data
		self.dst.resize((self.dst.size+self.trlen,))	
		self.size = self.dst.size
		self.dst[self.dst.size-self.trlen:] = samples
		
		return 0
