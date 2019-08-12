import nidaqmx
from tesdaq.listen import DeviceListener
from tesdaq.listen.parameters import TaskTypeRestriction

# Task types for use in later getattr() calls to nidaqmx device.
task_types = [
        "ai", # Analog Input
        "ao", # Analog Output
        "di", # Digital Input
        ]

def __map_enum_to_dict(enum_list):
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
def __volt_rng_as_nested_arr(vrange):
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
    ai_restriction, ai_backend = ai_task_restrict(device)
    # get digital input info
    di_restriction, di_backend = di_task_restrict(device)
    device_restrictions = {"analog_input": ai_restriction, "digital_input": di_restriction}
    backend_maps = {"analog_input": ai_backend, "digital_input": di_restriction}
    return device_restrictions, backend_maps
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
    backend_maps: dict
        Dict containing key, value pairs that map between named sample modes and their associated enum.
        Each key is the named argument of the TaskTypeRestriction, with each value containing the actual enum type.
    """
    chans = device.di_lines.channel_names
    trig_usage = __map_enum_to_dict(device.di_trig_usage)
    max_rate = device.di_max_rate
    min_rate = 0

    task_restrict = TaskTypeRestriction(
            num_tasks=1,
            valid_channels=chans,
            valid_timing=[], # TODO: fix timing
            valid_trigger=trig_usage.keys(),
            max_sample_rate=max_rate,
            min_sample_rate=min_rate,
            volt_ranges=[()], # TODO: fix volt range to be 0, logic_on
            sr_is_per_chan=True
            )
    backend_maps = {"trig_usage": trig_usage}

    return task_restrict, backend_maps
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
    backend_maps: dict
        Dict containing key, value pairs that map between named sample modes and their associated enum.
        Each key is the named argument of the TaskTypeRestriction, with each value containing the actual enum type.

    Notes
    -----
    backend_maps exists to associate named frontend arguments (strings such as CONTINUOUS) to their nidaqmx enum values.
    """
    chans = device.ai_physical_chans.channel_names
    samp_modes = __map_enum_to_dict(device.ai_samp_modes)
    trig_usage = __map_enum_to_dict(device.ai_trig_usage)
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
            valid_trig_usage=trig_usage.keys(),
            max_sample_rate=max_sample,
            min_sample_rate=min_sample,
            volt_ranges=volt_ranges,
            sr_is_per_chan=False #TODO: Add support for more tasks
            )
    backend_maps = {"valid_timing" : samp_modes, "valid_trigger": trig_usage}

    return task_restrict, backend_maps
    
class DAQmxListener(DeviceListener):
    def __init__(self,
            identifier,
            redis_instance,
            **kwargs):
        super(DAQmxListener, self).__init__(identifier, redis_instance, **kwargs)
        print(self.restrictions) 
    def configure(self, **kwargs):
        print(self.state) 
    def start(self):
        print("do nothing yet")
    def stop(self):
        print("stop")
