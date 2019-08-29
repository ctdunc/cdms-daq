import nidaqmx
from tesdaq.listen import DeviceListener
from tesdaq.listen.types import TaskRestriction

def map_enum_to_dict(enum_list):
    """__map_enum_to_dict
        Maps enum types to dict of {"name": enum} pairs, for use in frontend programming/TaskTypeRestriction generation.
    Parameters
    ----------
    enum_list: list of enum
        list of enum to generate dict from.
    Returns
    -------
    enum_dict: dict
        Dict containing {enum.name: enum} pairs.
    """
    enum_dict = {}
    for item in enum_list:
        enum_dict[item.name] = item
    return enum_dict 
def volt_rng_as_nested_arr(vrange):
    """__volt_rng_as_nested_arr
    Returns list of tuples containing (min,max) pairs of voltage ranges. 
    This function only exists because nidaqmx returns voltage ranges as one long list of [min_0,max_0,min_1,max_1...], instead of nesting them sensibly.
    Parameters
    ----------
    vrange: list
        Initial list of voltage ranges 
    Returns
    -------
    nice_ranges: list of tuple
        List of tuples containing min, max of nth voltage range.
    """
    nice_ranges = [(vrange[i], vrange[i+1]) for i in range(len(vrange)-1)][::2]
    return nice_ranges
def task_restrict_for_system():
    """task_restrict_for_system
    Gets task restriction for every device on a given system.

    Returns
    -------
    system_restrictions: dict
        Dict containing tuples of (device_restriction, backend_maps) pairs sorted by device name.
    """
    system = nidaqmx.system.system.System()
    devices = system.devices.device_names
    system_restrictions = {}
    for name in devices:
    # TODO: fix return type
        system_restrictions[name] = task_restrict_for_device(name)
    return system_restrictions
def task_restrict_for_device(devicename):
    """task_restrict_for_device
        Attempts to generate TaskTypeRestrictions for a given device.
    Parameters
    ----------
    devicename: str
        Name of device to attempt to generate restriction for.

    Returns
    -------
    """
    # TODO: fix return type
    device = nidaqmx.system.device.Device(devicename)
    # get analog input info
    ai_restriction = ai_task_restrict(device)
    # get digital input info
    di_restriction = di_task_restrict(device)
    device_restrictions = {"analog_input": ai_restriction, "digital_input": di_restriction}
    return device_restrictions
def di_task_restrict(device):
    """di_task_restrict
    Attempts to automatically generate a TaskTypeRestriction for a given NI devices digital input channels. 
    There's a good chance this won't work, since it appears that nidaqmx only adds channels to device when explicitly told to by user.
    If this function fails, you should manually add devices, etc to your device, and then call it again.
    Parameters
    ----------
    device: nidaqmx.system.device.Device
        Actual nidaqmx device to generate TaskTypeRestriction for.
    Returns
    -------
    task_restrict: tesdaq.listen.parameters.TaskTypeRestriction
        TaskTypeRestriction containing constraints on task
    """
    chans = device.di_lines.channel_names
    # Expand dict keys as list. This is so ast can parse() from RDB.
    trig_usage = [*__map_enum_to_dict(device.di_trig_usage)]
    max_rate = device.di_max_rate
    min_rate = 0

    task_restrict = TaskTypeRestriction(
            num_tasks=1,
            valid_channels=chans,
            valid_timing=[], # TODO: fix timing
            valid_trigger=trig_usage,
            max_sample_rate=max_rate,
            min_sample_rate=min_rate,
            volt_ranges=[()], # TODO: fix volt range to be 0, logic_on
            sr_is_per_chan=True
            )

    return task_restrict
def ai_task_restrict(device):
    """ai_task_restrict
    Attempts to automatically generate a TaskTypeRestriction for a given NI devices analog input channels. 
    There's a good chance this won't work, since it appears that nidaqmx only adds channels to device when explicitly told to by user.
    If this function fails, you should manually add devices, etc to your device, and then call it again.
    Parameters
    ----------
    device: nidaqmx.system.device.Device

    Returns
    -------
    task_restrict: tesdaq.listen.parameters.TaskTypeRestriction
        TaskTypeRestriction containing constraints on task
    """
    chans = device.ai_physical_chans.channel_names
    # Expand dict keys as list. This is so ast can parse() from RDB.
    # [*dict] -> [key1, key2, key3...]
    samp_modes = [*__map_enum_to_dict(device.ai_samp_modes)]
    trig_usage = [*__map_enum_to_dict(device.ai_trig_usage)]
    if device.ai_simultaneous_sampling_supported:
        max_sample = device.ai_max_multi_chan_rate
    else:
        max_sample = device.ai_max_single_chan_rate
    min_sample = device.ai_min_rate
    volt_ranges = __volt_rng_as_nested_arr(device.ai_voltage_rngs)

    task_restrict = TaskTypeRestriction(
            num_tasks=1, #TODO: Add support for more tasks
            valid_channels=chans,
            valid_timing=samp_modes,
            valid_trigger=trig_usage,
            max_sample_rate=max_sample,
            min_sample_rate=min_sample,
            volt_ranges=volt_ranges,
            sr_is_per_chan=False #TODO: Add support for more tasks
            )

    return task_restrict 
    
class DAQmxListener(DeviceListener):
    """DAQmxListener
    Abstract listener for devices using the NI-DAQmx driver.
    
    
    Attributes
    ----------
    Each attribute has a unique corresponding keyword that lets it be set from the redis database. 
    That keyword should **always** be exactly the name of the attribute (i.e., when CONFIG {'something': 10} is sent to the device's pubsub channel, on the next run of the wait loop, self.something = 10).
    """
    
    def __init__(self,
            identifier,
            redis_instance,
            device_name,
            **kwargs):
        # TODO: add support for multiple devices
        """__init__

        Parameters
        ----------
        identifier: str
            Unique string used to get and set values in redis database.
        redis_instance: redis.Redis
            Redis instance to connect
        device_name: str
            nidaqmx name of physical device (e.g. "Dev1").
        Keyword Args
        ------------
        analog_input: (tesdaq.listen.parameters.TaskTypeRestriction, dict of nidaqmx Enum)
            TaskTypeRestriction on 'analog_input' tasks. Corresponds to nidaqmx cfg_analog_input restrictions.
            If none, will attempt to autogenerate restrictions from current device settings. The nidaqmx enums should be named according to their functions in the TaskTypeRestriction.
            There will be an example of this soon.
        digital_input: tesdaq.listen.parameters.TaskTypeRestriction
            TaskTypeRestriction on 'digital_input' tasks.
            If none, will attempt to autogenerate restrictions from current device settings.
            It is suggested to explicitly pass these restrictions.
        """
        # TODO: Write example of passing dict of nidaqmx enum with kwarg
        if not kwargs:
            # If restriction passed as none, generate restriction
            device_restrictions = task_restrict_for_device(device_name)
        else:
            # Restriction = explicitly passed TaskTypeRestriction
            device_restrictions = kwargs 
        super(DAQmxListener, self).__init__(identifier, redis_instance, **kwargs)
        print(device_restrictions, self.restrictions)
        self.ai_task = nidaqmx.Task()
        self.di_task = nidaqmx.Task()
    def ai_encb(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        """ai_encb

        :param task_handle:
        :param every_n_samples_event_type:
        :param number_of_samples:
        :param callback_data:
        """

        raise NotImplementedError("Classes inheriting DAQmxListener must implement ai_encb() in order to use analog input tasks!")
    def di_encb(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        """di_encb

        :param task_handle:
        :param every_n_samples_event_type:
        :param number_of_samples:
        :param callback_data:
        """

        raise NotImplementedError("Classes inheriting DAQmxListener must implement di_encb() in order to use digital input tasks!")
    def configure_ai_task(self, channels, timing_mode, sample_rate): # TODO: add more args here, decide what "command" function should do.
        # Always recreate task (since diffing is handled by DeviceListener __configure method).
        if not self.ai_task.is_done():
            self.ai_task.close()
        self.ai_task = nidaqmx.Task()
        
        for channel in channels:
            # TODO: handle error if channel not valid
            self.ai_task.ai_channels.add_ai_voltage_chan(channel)
        
        # TODO: how to determine number of events/bin? Is this something we'd rather set on frontend, + have calculated frequency?
        # the numbers below are **super arbitrary**
        evt_per_trace = int(sample_rate/10) #TODO: STRICT floor function. This will offset if you put in a weird sample rate.
        trace_per_sec = 10

        self.ai_task.cfg_samp_clk_timing(sample_rate, sample_mode=timing_mode, samps_per_chan=evt_per_trace)
        self.ai_task.register_every_n_samples_acquired_into_buffer_event(evt_per_trace, self.ai_encb)
        return 0
    def configure_di_task(self): # TODO: add more args here, decide what "command" function should do.

        return 0
    def configure(self, **kwargs):
        print(self.state) 
        self.digital_input_task = nidaqmx.Task(identifier+"_di_task")
        self.analog_input_task = nidaqmx.Task(identifier+"_ai_task")
    def configure_analog_input_task(self, **kwargs):
        channels = kwargs['channels']
        sample_rate = kwargs['sample_rate']
        timing_mode = kwargs['timing_mode']
        for channel in channels:
            try:
                self.analog_input_task.ai_channels.add_ai_voltage_chan(channel)
            except nidaqmx.errors.DaqError as e:
                raise e
        try:
            timing_mode = nidaqmx.constants.AcquisitionType(timing_mode)
        except KeyError:
            raise ValueError("Timing mode \"{}\" is not a valid input for nidaqmx.constants.AcquisitionMode. This is likely an error with a manual task configuration. Please consult the ni documentation for further information".format(timing_mode))
        
        self.analog_input_task.timing.cfg_samp_clk_timing(
                sample_rate,
                sample_mode=timing_mode,
                samps_per_chan=int(sample_rate/10)) # TODO: more control over events per trace.
        self.analog_input_task.register_every_n_samples_acquired_into_buffer_event(int(sample_rate/10), self.__analog_input_callback)
    def analog_input_callback(
            self,
            task_handle, 
            every_n_samples_event_type,
            number_of_samples,
            callback_data):
        # TODO: fix
        return 0

            
        return 0 
    def configure_digitial_input_task(self, **kwargs):
        # TODO: config.
        return 0
    def configure(self):
        """configure
        Function that configures national instruments device from NI-DAQmx functions.
        Purposefully takes no arguments to ensure that NI config and redis state are always in sync.

        Returns
        -------
        Status
        """
        for key, value in self.state.items():
            if key == "analog_input":
                self.configure_analog_input_task(**value)
            if key == "digital_input":
                self.configure_digital_input_task(**value)
            # if key == "analog_output: TODO: Configure this
            # if key == "digital_output: TODO: configure
    def start(self):
        print("do nothing yet")
    def stop(self):
        print("stop")
