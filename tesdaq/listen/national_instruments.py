import nidaqmx as ni
import numpy as np 
from flask_socketio import SocketIO
from listen import DAQListener

class PCI6120(DAQListener):
    """PCI6120
    Class for control of National Instruments 6120 PCI Device.
    Extends DAQListener, so init method does the same thing.
    """

    def __init__(
            self,
            identifier,
            device_config,
            redis_instance):
        """__init__

        Parameters
        ----------
        identifier:
        device_config:
        redis_instance:
        """
        super(PCI6120, self).__init__(identifier, device_config, redis_instance)
    

    def __every_n_cb(
            self,
            task_handle,
            every_n_samples_event_type,
            number_of_sampels,
            callback_data):
        data = self.task.read(number_of_samples_per_channel=self.ept)
        print(data)
        if self.SOCKETIO_CONFIGURED:
            emit = []
            for channel in data:
                ## converts each trace on each channel to 32bit string for SIO transfer
                emit.append(np.float32(channel[::self.downsample_ratio]).tostring())
            self.sio.emit(self.channel, {'v': emit, 'l': len(emit[0])})

        if self.SAVEFILE_CONFIGURED:
            # do some save action
            print("TODO HERE")
        return 0

    def __configure_savefile(self, **kwargs):
        print("savefile", kwargs)

        return 0

    def __configure_socketio(self, **kwargs):
        print("sio", kwargs)
        self.sio = SocketIO(message_queue=message_queue)
        self.channel = channel
        self.SOCKETIO_CONFIGURED = True
        # TODO: Downsampling should configure here for SIO protocol.
        return 0
    def __configure_ni_task(self, **kwargs):
        """__configure_ni_task

        Parameters
        ----------
        **kwargs:
            Each keyword argument corresponds to a channel type, each of which has it's own configuration settings.
            e.g. 
            config.ANALOG_IN={
                channels: {
                    name: mode,
                    "Dev1/ai0": "read", 
                    "Dev1/ai7": "write"
                    },
                sample_rate: 100000,
                sample_mode: "continuous"
            },
            config.DIGITAL_IN={
                channels: {"Dev1/di0"},
                sample_rate: 10,
                sample_mode: "some_weird_trigger"
            }
                
        Returns
        -------
        """
        if self.task is None:
            self.task = ni.Task()
        elif not self.task.is_task_done():
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
                    self.task.ai_channels.add_ai_voltage_chan(channel)
                except ni.errors.DaqError as ni_error:
                    # TODO: Something with e. Logger?
                    print(ni_error)
        
        # Configure onboard sample clock timing of card
        self.task.timing.cfg_samp_clk_timing(
        self.task.cfg_samp_clk_timing(
            self.frq,
            sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=self.ept)
        # Register callback function for every trace.
        self.task.register_every_n_samples_acquired_into_buffer_event(self.ept, self.__every_n_cb)
        return 0

    def configure(self, **kwargs):
        if "ni_task" in kwargs:
            self.__configure_ni_task(**kwargs["ni_task"])
        if "socketio" in kwargs:
            self.__configure_socketio(**kwargs["socketio"])
        if "savefile" in kwargs:
            self.__configure_savefile(**kwargs["savefile"])
        return 0

    def start(self):
        self.task.start()
        return 0
    def stop(self):
        self.task.stop()
        return 0
