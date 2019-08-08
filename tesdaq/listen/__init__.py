name = "listen"

from redis import Redis
import inspect
import time
import re
import ast
from ..daq_constants import states, signals, config
from ..translate import redis_to_dict
from redis.exceptions import ConnectionError

class DAQListener:
    """DAQListener"""
    def __init__(
            self,
            identifier: str,
            device_config: dict,
            redis_instance: Redis):
        """__init__

        Parameters
        ----------
        identifier: str
            Unique string used to get and set values in redis database.
        device_config: dict
            Constraints on possible actions by DAQ. See doc/protocol.pdf for more information.
        redis_instance: redis.Redis
            Redis instance which listener should connect to.
        """
        
        self.id = config.DEV_KEY_PREFIX+identifier
        self.rdb_val = {"is_currently_running": False}
        self.r = redis_instance
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(identifier)
        # Checks for known config options and sets them if they're contained in device_config.
        for key, parameters in device_config.items():
            self.__set_chan_type_opt(key, **parameters)

        # Check if id is already in use 
        # Only do this on instantiation, as listener must be able to change value of own key later.
        val = self.r.get(self.id)
        if val:
            raise ValueError("A listener with id \"{}\" already exists. Please use a different id, or stop that worker, and unset the redis key.".format(self.id))
        else:
            self.r.set(self.id, str(self.rdb_val))

    def __set_chan_type_opt(
            self,
            channel_type,
            channels=[],
            max_sample_rate=1000,
            min_sample_rate=10,
            sr_is_per_chan=False,
            trigger_opts=[],
        ):
        """__set_chan_type_opt
        Sets allowable options for given channel type.

        Parameters
        ----------
        channel_type: str
            Type of channel to set option for (e.g. "analog input").
        channels: list
            Channels which are of type channel_type. Each channel should correspond to a physical location on the device (e.g. "Dev1/ai0" for an NI digitizer).
        max_sample_rate: int
            Maximum sample/write rate of given type.
        min_sample_rate: int
            Minimum sample/write rate of given type.
        sr_is_per_chan: bool
            Determines whether constraints should scale based on the number of active channels (i.e. true -> max sample rate of 800kS/s on one active channel is 400kS/s on two).
        trigger_opts: list
            List of strings detailing allowable trigger settings.
        """
        self.rdb_val[channel_type] = {
            "channels": channels,
            "max_sample_rate": max_sample_rate,
            "min_sample_rate": min_sample_rate,
            "sr_is_per_chan": sr_is_per_chan,
            "trigger_opts": trigger_opts
        }
    def __compare_update_rdb(self):
        """compares local state to redis database state, and updates redis with any differences"""
        db_val = redis_to_dict(self.r.get(self.id))
        if db_val != self.rdb_val:
            self.r.set(self.id, str(self.rdb_val))
    def __update_run_state(self, sig):
        """__update_run_state
            Checks incoming signal to determine what run state is. 
            Run state determines whether config(), start() can be called, 
            as updating task configurations while DAQ is active can lead to hardware failure on some devices.

        Parameters
        ----------
        sig: str
            Signal that determines what current state should be.
        """
        if sig == signals.START:
            self.rdb_val['is_currently_running'] = True
        if sig == signals.STOP:
            self.rdb_val['is_currently_running'] = False
    def configure(self, **kwargs):
        """configure
        executed when signals.CONFIG is recieved in wait() loop.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self, **kwargs):
        """start
        executed when signals.START is recieved in wait() loop.
        Inheriting classes should be sure long-polling actions taken in this function execute **asynchronously**, otherwise task state will fail to update.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement start()".format(type(self).__name__))
    def stop(self, **kwargs):
        """stop
        executed when signals.STOP is recieved in wait() loop.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement stop()".format(type(self).__name__))
    def wait(self):
        """starts loop which checks redis database for status updates and executes commands on reception"""
        while True:
            self.__compare_update_rdb()
            message = self.pubsub.get_message()
            if message:
                command = message['data']
                try:
                    command = str(command.decode("utf-8"))
                except AttributeError as e:
                    command = str(command)
                passed_args = redis_to_dict(command)
                if command.startswith(signals.START):
                    self.start(**passed_args)
                    self.__update_run_state(signals.START)
                if command.startswith(signals.CONFIG):
                    self.configure(**passed_args)
                if command.startswith(signals.STOP):
                    self.__update_run_state(signals.STOP)
                    self.stop(**passed_args)
            time.sleep(.1)


class TestListener(DAQListener):
    def __init__(self, device_name, device_config, redis_instance, **kwargs):
        super(TestListener, self).__init__(device_name, device_config, redis_instance, **kwargs)
    def configure(self, **kwargs):
        print("RECIEVED MESSAGE CONFIG", kwargs)
        return 0
    def start(self, **kwargs):
        print("RECIEVED MESSAGE START", kwargs)
        return 0
    def stop(self, **kwargs):
        print("RECIEVED MESSAGE STOP", kwargs)
        return 0
