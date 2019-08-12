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
    output = {}
    for item in enum_list:
        output[item.name] = item
    return output
def __volt_rng_as_nested_arr(vrange):
    return [(vrange[i], vrange[i+1]) for i in range(len(vrange)-1)][::2]
def task_restrict_for_system():
    system = nidaqmx.system.system.System()
    devices = system.devices.device_names
    restrictions = []
    for name in devices:
    # TODO: fix return type
        restrictions.append(task_restrict_for_device(name))
    return 0
def task_restrict_for_device(devicename):
    # TODO: fix return type 
    device = nidaqmx.system.device.Device(devicename)
    
    # get analog input info
    ai_restriction, ai_backend = ai_task_restrict(device)
    # get digital input info
    di_restriction, di_backend = di_task_restrict(device)
    restrictions = {"analog_input": ai_restriction, "digital_input": di_restriction}
    backend_maps = {"analog_input": ai_backend, "digital_input": di_restriction}
    return restrictions, backend_maps
def di_task_restrict(device):
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

    def configure(self, **kwargs):
        print(self.state) 
    def start(self):
        print("do nothing yet")
    def stop(self):
        print("stop")
