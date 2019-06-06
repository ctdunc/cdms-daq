import nidaqmx as ni
import h5py as hp
import numpy as np
import time

class AIDAQ(ni.Task):
	def __init__(self, **kwargs):		
		""" 
		meaningful keyword args:
			daq related:
			- card model (sets trlen, sr)
			- sr (sample rate) (overrides card model)
			- tr (trace length) (in samples, overrides model)
			- device (channel, device, i.e. Dev1/ai0)

			data save related
			- savefile (must end in .h5)
			- group (optional, set to 'traces' if none)
			- dataset (none, or dict with parameter names)
		"""
		# initialize self as nidaqmx task object
		ni.Task.__init__(self)

		# handle setting default values dynamically, so that further keys can be added later
		# with more advanced behavior/priority in setting defaults
		model	=	{
					"NI6120": 8e5,
					"NI6374": 3.5e6
				}
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
