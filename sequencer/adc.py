import nidaqmx
import numpy as np

def continuous_data(sample_rate, channels, h5file=None, dataset="data", **kwargs):
    """
    Returns nidaqmx.Task object which can be started or stopped at will.
    
    Arguments:
    ----------
    sample_rate:        rate in Hz at which samples will be taken.
    channels:           list of strings denoting channels.
    

    Keyword Arguments
    -----------------
    h5file:             hdf5 file object to write data into. 
                        If none, it will simply print data when returned task is started.
    dataset:            title of dataset to save data in.
    
    """
    task = nidaqmx.Task()
    for c in channels:
        task.ai_channels.add_ai_voltage_chan(c)

    task.timing.cfg_samp_clk_timing(sample_rate,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=sample_rate)
    if h5file:
        dst = h5file.create_dataset(dataset, [None for i in channels], 'f')
        def handle_read_data(data):
            print(data) 
    else:

        def handle_read_data(data):
            print(np.asarray(data).shape)
    def every_n_callback(task_handle,
            every_n_samples_event_type,
            number_of_samples,
            callback_data):

        readout = task.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
        # TODO: h5file write or print
        handle_read_data(readout)

        return 0
    
    task.register_every_n_samples_acquired_into_buffer_event(int(sample_rate/2),every_n_callback)
        
    return task 

def finite_randoms():
    
    return 0

def external_trigger(sample_rate, channels, trigger_source, h5file=None, dataset="data", **kwargs):
    task = nidaqmx.Task()
    for c in channels:
        task.ai_channels.add_ai_voltage_chan(c)

    task.timing.anlg_edge_start_trig(trigger_source=trigger_source)
    if h5file:
        dst = h5file.create_dataset(dataset, [None for i in channels], 'f')
        def handle_read_data(data):
            print(data) 
    else:
        def handle_read_data(data):
            print(np.asarray(data).shape)
    def every_n_callback(task_handle,
            every_n_samples_event_type,
            number_of_samples,
            callback_data):

        readout = task.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
        # TODO: h5file write or print
        handle_read_data(readout)

        return 0
    
    task.register_every_n_samples_acquired_into_buffer_event(int(sample_rate/2),every_n_callback)
        
    return task 
    return 0
