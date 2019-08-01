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
    def __init__(
            self,
            identifier,
            device_config,
            redis_instance,
            redis_channels=['default'],
            **kwargs):
        """ Abstraction for listening to redis messages to execute DAQ commands
        Also defines necessary startup procedures to make sure everybody communicating with
        the database knows what tasks are defined where.

        Arguments:
        ----------
        identifier:    specifies redis KEY corresponding to device config.
        device_config:  required parameter that gets turned into json as allowable things the device may do (see doc/protocol.pdf for an explanation).
        redis_channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).
        """
        
        self.id = "_tesdaq.dev."+identifier
        self.redis_channels = redis_channels
        self.rdb_val = {"is_currently_running": False}
        self.r = redis_instance
        self.pubsub = self.r.pubsub()
        for c in redis_channels:
            self.pubsub.subscribe(c)
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
            max_sample_rate=1000, # hz
            min_sample_rate=10,
            sr_is_per_chan=False,
            trigger_opts=[],
        ):
        """
        Should take in keyword args defined in doc/protocol.pdf section 3.1
        This implementation *only* sets values in the redis database.
        Inheriting classes should define this function,
        unless they use the default channel types outlined in doc/protocol.pdf
        """
        self.rdb_val[channel_type] = {
            "channels": channels,
            "max_sample_rate": max_sample_rate,
            "min_sample_rate": min_sample_rate,
            "sr_is_per_chan": sr_is_per_chan,
            "trigger_opts": trigger_opts
        }
    def configure(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement start()".format(type(self).__name__))
    def stop(self, **kwargs):
        # Should only take in keyword args as a parameter,
        # that will be passed as JSON to Redis from client end
        raise NotImplementedError("class {} must implement stop()".format(type(self).__name__))
    def wait(self):
        while True:
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
                if command.startswith(signals.CONFIG):
                    self.configure(**passed_args)
                if command.startswith(signals.STOP):
                    self.stop(**passed_args)
            time.sleep(1)


class TestListener(DAQListener):
    def __init__(self,device_name, device_config, redis_instance, **kwargs):
        super(TestListener, self).__init__(device_name,device_config, redis_instance, **kwargs)
    def configure(self, **kwargs):
        print("RECIEVED MESSAGE CONFIG", kwargs)
        return 0
    def start(self, **kwargs):
        print("RECIEVED MESSAGE START", kwargs)
        return 0
    def stop(self, **kwargs):
        print("RECIEVED MESSAGE STOP", kwargs)
        return 0

