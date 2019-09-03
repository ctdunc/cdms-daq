name = 'types'
import warnings
from collections import namedtuple

def _warn_invalid(value, parameter):
    warnings.warn("Value \"{}\" is not allowed by restriction on \"{}\".".format(value, parameter))
    return 0
"""TaskRestriction
Tuple subclass that stores immutable, device specific information about constraints on task types.
e.g., if a DAQ can run one analog voltage task at a time, num_tasks=1.

Parameters
----------
num_tasks: int
    Number of tasks of same type that can be run simultaneously (currently always set to 1 for NI task).
valid_channels: list of str
    List containing valid channel paths for task type.
valid_timing: list of str
    List containing valid timing configurations for task type.
valid_trigger: list of str
    List containing valid trigger usages for current task type.
max_sample_rate: int
    Maximum sample rate for task type.
min_sample_rate: int
    Minimum sample rate for task type.
volt_ranges: list of tuple of float
    list of pairs of integers denoting (min, max) of given voltage range.
sr_is_per_chan: bool
    Whether sample rate scales as 1/channel. Default=False.
"""
TaskRestriction = namedtuple(
        'TaskRestriction',
        [   'num_tasks',
            'valid_channels',
            'valid_timing',
            'valid_trigger',
            'max_sample_rate',
            'min_sample_rate',
            'volt_ranges',
            'sr_is_per_chan'
        ]
)

class TaskState:
    """TaskState
    Class that handles management of task state, and validation against restrictions.

    Parameters
    ----------
    restriction: tesdaq.parameters.TaskTypeRestriction
    channels: list of str
        Default list of channels to add to task. Can be empty, cannot be none.
    sample_rate: int
        Default rate to sample/generate samples. Defaults to 100S/s.
    timing_mode: str
        Default timing mode. 

    Attributes
    ----------
    current_state: dict
        returns dict containing channels, sample rate, timing mode and is active.
    restrict: DeviceRestriction
        property set by 'restriction' argument of __init__
    channels: list of str
        Contains list of channels currently in task. Setter automatically validates against object restriction and dedupes.
    sample_rate:
        Sample rate of current task. Setter automatically checks range.
    timing_mode:
        Timing mode of current task. Setter automatically checks against restriction.

    Notes
    -----
    Code pattern for resetting channels should go as
    ```python
        del taskstate.channels
        taskstate.channels = [...new channels...]
    ```
    """
    def __init__(
            self,
            restriction,
            ):
        self.restrict = restriction
        self.__channels = [] # Start with all channels disabled.
        self.__sample_rate = getattr(restriction, 'min_sample_rate') # Start at minimum sample rate
        self.__trigger_mode = getattr(restriction,'valid_trigger')[0]
        self.__timing_mode = getattr(restriction, 'valid_timing')[0]
        self.__volt_range = getattr(restriction, 'volt_ranges')[0]
        self.is_active = False


    #CHANNELS PROPERTY
    @property
    def channels(self):
        return self.__channels
    @channels.setter
    def channels(self, channels):
        """
        adds new channels from input array. 
        Avoids duplication and checks validity against constraint.
        If you need to clear channel array, call `del TaskState.channels` first.

        Parameters
        ----------
        channels: list of str
            Contains all channels to activate for specific task.

        Returns
        -------
        """
        for channel in channels:
            if channel not in getattr(self.restrict, "valid_channels"): 
                raise ValueError("Channel \"{}\" is not allowed by the current restriction.".format(channel))
                
        if len(channels) > 0:
            self.__channels = channels 

    # SAMPLE RATE PROPERTY 
    # TODO, add check on sr_is_per_chan
    @property
    def sample_rate(self):
        return self.__sample_rate
    @sample_rate.setter
    def sample_rate(self, sample_rate):
        msr = getattr(self.restrict, 'min_sample_rate')
        mxr = getattr(self.restrict, 'max_sample_rate')
        if msr <= sample_rate <= mxr:
            self.__sample_rate = sample_rate
        else:
            raise ValueError("Sample rate is outside valid range")

    # TIMING MODE PROPERTY
    @property
    def timing_mode(self):
        return self.__timing_mode
    @timing_mode.setter
    def timing_mode(self, timing_mode):
        if timing_mode in getattr(self.restrict, 'valid_timing'):
            self.__timing_mode = timing_mode
        else:
            raise ValueError("Timing mode \"{}\" is not allowed by current restriction".format(timing_mode))
    
    # VOLT RANGE PROPERTY
    @property
    def volt_range(self):
        return self.__volt_range

    @volt_range.setter
    def volt_range(self, volt_range):
        if volt_range in getattr(self.restrict, 'volt_ranges'):
            self.__volt_range = volt_range
        else:
            _warn_invalid(volt_range, 'volt_ranges')
   
    # TRIGGER MODE PROPERTY
    @property
    def trigger_mode(self):
        return self.__trigger_mode

    @trigger_mode.setter
    def trigger_mode(self, trigger_mode):
        if trigger_mode in getattr(self.restrict, 'valid_trigger'):
            self.__trigger_mode = trigger_mode
        else:
            _warn_invalid(trigger_mode, 'valid_trigger')
