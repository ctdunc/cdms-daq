<<<<<<< HEAD
import nidaqmx as ni
import numpy as np 
from flask_socketio import SocketIO
from listen.daq_listen import DAQListener
=======
<<<<<<< HEAD
import nidaqmx as ni
import numpy as np 
from flask_socketio import SocketIO
from daq_listener import DAQListener
=======
# import nidaqmx as ni
import numpy as np 
from flask_socketio import SocketIO
from listen.daq_listen import DAQListener
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7

class NI6120(DAQListener):
    def __init__(
            self,
            ai_chans,
            evt_per_trace,
            trace_per_sec,
            **kwargs):
        """
        Class for remote management of national instruments 6120 digitizer.
<<<<<<< HEAD
=======
<<<<<<< HEAD
        Likely could benefit from abstraction/work for other devices.

        Arguments 
=======

        Arguments
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        -----------
        evt_per_trace:  number of samples taken *per channel* per trace.
        trace_per_sec:  number of traces taken per second.
        ai_chans:       array of channels to take data from (e.g. Dev1/ai0).
        """
        super(NI6120, self).__init__(**kwargs)
<<<<<<< HEAD
        self.task = None
        self.SOCKETIO_CONFIGURED = False
        self.SAVEFILE_CONFIGURED = False
=======
        self.SOCKETIO_CONFIGURED = False
        self.SAVEFILE_CONFIGURED = False
<<<<<<< HEAD

        self.ept = evt_per_trace
        self.tps = trace_per_sec
        self.frq = self.ept*self.tps # Frequency (samples/second).
        self.downsample_ratio = np.ceil(self.ept/1000)
        self.task = ni.Task()

        for channel in ai_chans:
            try:
                self.task.ai_channels.add_ai_voltage_chan(channel)
            except ni.errors.DaqError as e:
                raise e
        self.task.cfg_samp_clk_timing(
            self.frq,
            sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=self.ept)
        self.task.register_every_n_samples_acquired_into_buffer_event(self.ept, self.__every_n_cb)
=======
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        
        self.__configure_ni_task(
            ai_chans=ai_chans,
            evt_per_trace=evt_per_trace,
            trace_per_sec=trace_per_sec
            )
<<<<<<< HEAD
=======
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a

>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
    def __every_n_cb(
            self,
            task_handle,
            every_n_samples_event_type,
            number_of_sampels,
            callback_data):
<<<<<<< HEAD
=======
<<<<<<< HEAD
        d = self.task.read(number_of_samples_per_channel=self.ept)
        print(d)
        if self.SOCKETIO_CONFIGURED:
            emit = []
            for data in d:
                emit.append(np.float32(data[::self.downsample_ratio]).tostring())
=======
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        data = self.task.read(number_of_samples_per_channel=self.ept)
        print(data)
        if self.SOCKETIO_CONFIGURED:
            emit = []
            for channel in data:
                ## converts each trace on each channel to 32bit string for SIO transfer
                emit.append(np.float32(channel[::self.downsample_ratio]).tostring())
<<<<<<< HEAD
=======
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
            self.sio.emit(self.channel, {'v': emit, 'l': len(emit[0])})

        if self.SAVEFILE_CONFIGURED:
            # do some save action
            print("TODO HERE")
        return 0
<<<<<<< HEAD
    def __configure_savefile(self, **kwargs):
        print("savefile", kwargs)
=======
<<<<<<< HEAD
    def __configure_savefile(self, filepath):
=======

    def __configure_savefile(self, **kwargs):
        print("savefile", kwargs)
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        """
        Configures save location + protocol for data. Yet to be implemented.
        """

        return 0

<<<<<<< HEAD
=======
<<<<<<< HEAD
    def __configure_socketio(self, message_queue, channel):
        """
        Configures Socketio
        Parameters
=======
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
    def __configure_socketio(self, **kwargs):
        print("sio", kwargs)
        """
        Configures Socketio

        Keyword Args
<<<<<<< HEAD
=======
>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        ----------
        message_queue:  message queue for socketio instance (e.g. "redis://")
        channel:        socketio namespace on which to emit events (e.g. "newTrace")
        """
        self.sio = SocketIO(message_queue=message_queue)
        self.channel = channel
        self.SOCKETIO_CONFIGURED = True
<<<<<<< HEAD
        # TODO: Downsampling should configure here for SIO protocol.
        return 0

=======
<<<<<<< HEAD

        return 0
    def configure(self):
=======
        # TODO: Downsampling should configure here for SIO protocol.
        return 0
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
    def __configure_ni_task(self, **kwargs):
        print("ni", kwargs)
        """
        Stops current NI task, updates parameters, and restarts.

        Keyword Args
        ----------
        evt_per_trace:  number of samples taken *per channel* per trace.
        trace_per_sec:  number of traces taken per second.
        ai_chans:       array of channels to take data from (e.g. Dev1/ai0).
        """
        # Create NI task if one doesn't exist. Stop it if it does.
        if self.task is None:
            self.task = ni.Task()
<<<<<<< HEAD
        elif not self.task.is_task_done():
=======
        else if not self.task.is_task_done():
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
            self.task.stop()
        if "evt_per_trace" in kwargs:
            self.ept = kwargs["evt_per_trace"]
            print(self.ept)
        if "trace_per_sec" in kwargs:
            self.tps = kwargs["trace_per_sec"]
            print(self.tps)

        self.frq = self.ept*self.tps # Frequency (samples/second).

        if "ai_chans" in kwargs:
            for channel in kwargs["ai_chans"]:
                try:
                    print(channel)
<<<<<<< HEAD
                    self.task.ai_channels.add_ai_voltage_chan(channel)
=======
                    # self.task.ai_channels.add_ai_voltage_chan(channel)
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
                except ni.errors.DaqError as ni_error:
                    # TODO: Something with e. Logger?
                    print(ni_error)
        
        # Configure onboard sample clock timing of card
<<<<<<< HEAD
        self.task.timing.cfg_samp_clk_timing(
=======
        self.task.cfg_samp_clk_timing(
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
            self.frq,
            sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=self.ept)
        # Register callback function for every trace.
        self.task.register_every_n_samples_acquired_into_buffer_event(self.ept, self.__every_n_cb)
        return 0

    def configure(self, **kwargs):
        """
        Callback for redis CONFIG signal. Configures task according to keyword arguments.
        
        Keyword Arguments
            Each Keyword Argument should contain a dict with the various arguments to be passed to certain callback functions.
        ----------
        ni_task:        Contains arguments to be passed to __configure_ni_task()
        socketio:       Contains arguments to be passed to __configure_socketio()
        savefile:       Contains arguments to be passed to __configure_savefile()
        """
        if "ni_task" in kwargs:
            self.__configure_ni_task(**kwargs["ni_task"])
        if "socketio" in kwargs:
            self.__configure_socketio(**kwargs["socketio"])
        if "savefile" in kwargs:
            self.__configure_savefile(**kwargs["savefile"])
<<<<<<< HEAD
        return 0
    def start(self):
        self.task.start()
        return 0
    def stop(self):
        print("stopping")
        self.task.stop()
=======

>>>>>>> 3162c8570790777b5d028de90dc3db5fa0eb0c3a
        return 0
    def start(self):
        return 0
    def stop(self):
>>>>>>> a6844dddb35b52511201ba41ed24c9eda489a9f7
        return 0
