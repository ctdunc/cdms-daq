"""TODO:
    finish dosctring
"""
import redis
import inspect
import time
import re
import ast
from ..daq_constants import states, signals, config
class DAQListener:
    def __init__(
            self,
            identifier,
            redis_channels=['def'],
            redis_host='localhost',
            redis_password='',
            redis_port=6379,
            redis_database=0,
            **kwargs):

        """ Abstraction for listening to redis messages to execute DAQ commands

        Arguments:
        ----------
        identifier: Unique ID used to store device metadata in Redis DB.
        channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).
        """
        self.id = identifier
        self.redis_channels = redis_channels

        self.allowable_config['ai_channels'] = kwargs.get('ai_chans', None) 
        self.allowable_config['di_channels'] = kwargs.get('di_chans', None)
        self.allowable_config['ao_channels'] = kwargs.get('ao_chans', None)
        self.allowable_config['di_channels'] = kwargs.get('do_chans', None)

        # Make sure that these exist, so they can be set when the worker is turned on
        try:
            self.r = redis.Redis(
                host=redis_host,
                password=redis_password,
                port=redis_port,
                db=redis_database
                )
            self.pubsub = r.pubsub()
            for c in redis_channels:
                self.pubsub.subscribe(c)
            self.STATE = states.WAIT
        # TODO: More specific exception here
        except Exception as e:
            self.STATE = states.REDIS_FAILURE
            print(e)
        
        # Check for optional functions, and send the frontend those allowable parameters
        self.allowable_config = {}
        for val in config.CHAN_CFG:
            func = getattr(self, val, None)
            if callable(func):
                self.allowable_config[val] = inspect.getfullargspec(func)
        
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
    def set_allowable_config(self):
        self.r.set(self.id, self.allowable_config)

    def wait(self):
        while self.STATE == states.WAIT:
            message = self.pubsub.get_message()
            if message:
                command = message['data']
                try:
                    command = str(command.decode("utf-8"))
                except AttributeError as e:
                    command = str(command)
                passed_args = _to_dict(command)
                if command.startswith(signals.START):
                    self.start(**passed_args)
                if command.startswith(signals.CONFIG):
                    self.configure(**passed_args)
                if command.startswith(signals.STOP):
                    self.stop(**passed_args)
                if command.startwith(signals.UPDATE_CFG):
                    self.set_allowable_config():
            time.sleep(1)

class TestListener(DAQListener):
    def __init__(self, **kwargs):
        super(TestListener, self).__init__(**kwargs)
    
    def cfg_analog_input(self,**kwargs):
        print("your mom")
    def configure(self, **kwargs):
        print("RECIEVED MESSAGE CONFIG", kwargs)
        return 0
    def start(self, **kwargs):
        print("RECIEVED MESSAGE START", kwargs)
        return 0
    def stop(self, **kwargs):
        print("RECIEVED MESSAGE STOP", kwargs)
        return 0

def _to_dict(st):
    """
    Convienence Method to return Dict from Redis input
    """
    dict_string = re.search('({.+})', st)
    if dict_string:
        return ast.literal_eval(dict_string.group(0))
    else:
        return {}

