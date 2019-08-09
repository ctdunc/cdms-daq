import ast
import re
from collections import namedtuple
"""DeviceRestriction
Tuple subclass that stores immutable, device specific information about constraints on task types.
e.g., if a DAQ can run one analog voltage task at a time, num_tasks=1.

Parameters
----------
num_tasks: int
    
valid_channels: list of str

valid_timing: dict

max_sample_rate:

min_sample_rate:

sr_is_per_chan:
"""
DeviceRestriction = namedtuple(
        'DeviceRestriction', 
        ['num_tasks',
        'valid_channels',
        'valid_timing',
        'max_sample_rate',
        'min_sample_rate',
        'sr_is_per_chan']
)

class TaskState:
    """TaskState
    Class that handles management of task state, and validation against restrictions.

    Parameters
    ----------
    restriction: DeviceRestriction
    channels: list of str
        Default list of channels to add to task. Can be empty. 
    sample_rate: int
        Default rate to sample/generate samples.
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
            channels=[],
            sample_rate=100,
            timing_mode='continuous'
            ):
        self.__restrict = restriction
        self.channels = channels
        self.sample_rate = sample_rate
        try:
            self.timing_mode = timing_mode
        except ValueError:
            self.timing_mode = self.__restrict['valid_timing'][0]

        self.__is_active = False
    def __str__(self):
        return str(self.__dict__)
    @property
    def current_state(self):
        state_dict = {
                'channels': self.channels, 
                'sample_rate': self.sample_rate,
                'timing_mode': self.timing_mode,
                'is_active': self.is_active
                }
        return state_dict
    @property
    def is_active(self):
        return self.__is_active

    @property
    def restrict(self):
        return self.__restrict

    @property
    def channels(self):
        return self.__channels

    @property
    def sample_rate(self):
        return self.__sample_rate

    @property
    def timing_mode(self):
        return self.__timing_mode

    @channels.deleter
    def channels(self):
        self.__channels = []

    @channels.setter
    def channels(self, channels):
        """
        adds new channels from input array. 
        Avoids duplication and checks validity against constraint.
        If you need to clear channel array, call `del taskState.channels` first.

        Parameters
        ----------
        channels: list of str
            Contains all channels to activate for specific task.

        Returns
        -------
        """
        try:
            next_channels = self.channels
        except AttributeError:
            next_channels = []
            self.__channels = next_channels
        for channel in channels:
            if channel not in getattr(self.restrict, "valid_channels"): 
                raise ValueError("Channel \"{}\" is not allowed by the current restriction.".format(channel))
            elif channel not in next_channels:
                next_channels.append(channel)
        if len(next_channels) > 0:
            self.__channels = next_channels

    @sample_rate.setter
    def sample_rate(self, sample_rate):
        msr = getattr(self.restrict, 'min_sample_rate')
        mxr = getattr(self.restrict, 'max_sample_rate')
        if msr < sample_rate < mxr:
            self.__sample_rate = sample_rate
        else:
            raise ValueError("Sample rate is outside valid range")
    @timing_mode.setter
    def timing_mode(self, timing_mode):
        if timing_mode in getattr(self.restrict, 'valid_timing'):
            self.__timing_mode = timing_mode
        else:
            raise ValueError("Timing mode \"{}\" is not allowed by current restriction".format(timing_mode))

def redis_to_dict(redis_string):
    """redis_to_dict
    Translates (byte)string from redis database to dict object.

    Parameters
    ----------
    redis_string: str
        String recieved from redis database.

    Returns
    -------
    redis_dict: dict
        Dict of values from redis db. Typically corresponds to device state or restriction.
    """
    try:
        redis_string = redis_string.decode("utf-8")
    except AttributeError:
        pass

    dict_string = re.search('({.+})', st)
    if dict_string:
        redis_dict = ast.literal_eval(dict_string.group(0))
        return redis_dict
