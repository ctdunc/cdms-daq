import nidaqmx as ni
import numpy as np
from flask_socketio import SocketIO
from celery import Task

class NI6120(Task):
    ignore_result = True
    
    def __init__(self, 
            evt_per_trace, 
            trace_per_sec, 
            ai_chans):
        """
        Class for remote management of national instruments 6120 digitizer.
        Likely could benefit from abstraction/work for other devices.

        Parameters
        -----------
        evt_per_trace:  number of samples taken *per channel* per trace.
        trace_per_sec:  number of traces taken per second.
        ai_chans:       array of channels to take data from (e.g. Dev1/ai0).
        socket:         
        """

        self.SOCKETIO_CONFIGURED = False
        self.SAVEFILE_CONFIGURED = False

        self.ept = evt_per_trace
        self.tps = trace_per_sec
        self.frq = self.ept*self.tps # Frequency (samples/second).
        self.downsample_ratio = np.ceil(self.ept/1000)
        
        self.task = ni.Task()

        for channel in ai_chans:
            try:
                self.task.ai_channels.add_ai_voltagechan(channel)
            except ni.errors.DaqError as e:
                raise e
        self.task.cfg_samp_clk_timing(
                self.frq, 
                sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                samps_per_chan=self.ept)
        self.task.register_every_n_samples_acquired_into_buffer_event(self.ept, self.__every_n_cb)

    def __every_n_cb(self, 
            task_handle, 
            every_n_samples_event_type, 
            number_of_sampels, 
            callback_data):
    
        d = self.task.read(number_of_samples_per_channel=self.ept)
        print(d)
        
        if self.SOCKETIO_CONFIGURED:
            emit = []
            for data in d:
                emit.append(np.float32(data[::self.downsample_ratio]).tostring())
            self.sio.emit(self.channel, {'v': emit, 'l': len(emit[0])})

        if self.SAVEFILE_CONFIGURED:
            # do some save action
            print("TODO HERE")
        return 0
    
    def configure_savefile(self, filepath):
        """
        Configures save location + protocol for data. Yet to be implemented.
        """

        return 0

    def configure_socketio(self, message_queue, channel):
        """
        Configures Socketio 
        Parameters
        ----------
        message_queue:  message queue for socketio instance (e.g. "redis://")
        channel:        socketio namespace on which to emit events (e.g. "newTrace")
        """
        self.sio = SocketIO(message_queue=message_queue)
        self.channel=channel
        self.SOCKETIO_CONFIGURED = True

        return 0

    def run(self, source, *args, **kwargs):
        self.source = source
        
        self.task.start()
        
