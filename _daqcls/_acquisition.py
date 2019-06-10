import nidaqmx as ni
import h5py as hp
import numpy as np
import time


class AIVoltageDAQ(ni.Task):
    """
    Class that acquires voltage measurement
    -------------------
    Parameters:
    -------
    - sr:       sample rate. determines precise no. samples/sec
    - tr:       trace length. different behavior for continuous, finite measurement. See documentation for each class for specifics.
    - device:   nidaqmx pointer to physical device. ex: 'Dev1/ai0'
    - savefile: hdf5 savefile. if no file is provided, data will not be saved.
    - group:    group within hdf5 savefile. default is '/'
    -------
    """
    def __init__(
            self, 
            sr, # sample rate
            tr, # trace length
            device, # NI Channel name
            savefile='', # HDF5 file to save data
            group=''    # HDF5 group in which save datasets
            ):

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

            self.dataset    =   self.group.create_dataset(
                                    'ai_'+str(time.time()),
                                    (self.trlen,),
                                    maxshape=(None,)
                                    )
        else:
            self.SAVE       =   False
            print('no savefile specified. data will be lost')

        ##############################  
        # NI task configuration
        ##############################
        ni.Task.__init__(self)                              # start NI task object

        self.device     =   device                          # may be useful to access later.
        self.ai_channels.add_ai_voltage_chan(self.device)   # creates analog input voltage channel at specified device

        return 0 


    def save_data(self, samples):
        if self.SAVE:
            self.dataset.resize((self.dataset.size+self.tr,))
            self.dataset[self.dataset.size-self.tr:]    =   samples
        
        return 0



class ContVoltDAQ(AIVoltageDAQ):

        """
        Continuous Volatage Data AcQuisition extends __VDAQ
        ---------
        Parameters:

        """
    def __init__(self):

    AIVoltageDAQ.__init__(self) 

        self.timing.cfg_samp_clk_timing(
            self.sr,
            sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=self.sr
            )
        
        self.register_every_n_samples_acquired_into_buffer_event(
                self.trlen,
                self.__every_n_cb
                )
        return 0
        
    def __every_n_cb(self, task_handle, every_n_samples_event_type,
                number_of_samples, callback_data):
        samples =   self.read(number_of_samples_per_channel=self.trlen)
        self.save_data(samples)
        return 0
        
        """OLD CODE
	# initializes config variables based on class parameters. 
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
                """
