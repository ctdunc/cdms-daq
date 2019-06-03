import nidaqmx as ni
import h5py as hp
import numpy as np
import time

class AIDAQ(ni.Task):
	def __init__(
		self,			# hardcoded default sample rate of 100kS/s. 
		model="",		# typically, you should provide either the device model or sample rate.
		sr=1e5,			# if you wish to provide a sample rate other than the max specified by
		trlen=0,		# your card, leave model blank.
		device="Dev1/ai0",
		savefile="test.h5"
		):		

			
			
		# init task
		ni.Task.__init__(self)
		# hardcoded max sample rates according to card model	
		sr_len_by_model =	{
					"NI6120": 8e5,
					"NI6374": 3.5e6
					}

		self.sr		=	int(sr_len_by_model.get(model, sr))  # set sample rate.

		if trlen==0:
			self.trlen=self.sr	# trace length is equal to sample rate by default
		else:				# (i.e. each trace is one second long).
			self.trlen=trlen
									

		self.dt		= 	1./self.sr			# time resolution
		self.df		=	self.sr/self.trlen		# frequency resolution

		self.device	=	device
		self.savefile	=	hp.File(savefile,'a')		# opens file object, creates if not exists
		try:
			self.grp	=	self.savefile.create_group('traces')
		except ValueError:
			self.grp	=	self.savefile['traces']
			print("group traces exists, skipping")
		self.dst	=	self.grp.create_dataset(
						'ai_'+model+'_'+str(time.localtime()),
						(self.trlen,),
						chunks=(60*self.sr,),	# chunks in 1 minute interval
						maxshape=(None,)
						)

	def begin_daq(self):
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
		samples = self.read(number_of_samples_per_channel=self.trlen)

		self.__save_data(samples)	
		

		return 0

	def __save_data(self, samples):
		# resize dataset to accept new data
		self.dst.resize((self.dst.size+self.trlen,))	
		self.dst[self.dst.size-self.trlen:] = samples
		
		return 0

test = AIDAQ(trlen=10000,sr=6e5)
test.begin_daq()
test.start()

input("test running. press enter to stop")
