from ..daq_constants import states, signals, config
from ..translate import redis_to_dict
import redis
import time
import re

class DAQCommander:
    def __init__(
            self,
            redis_instance,
            **kwargs):

        """ Convenience class to issue Redis messages to execute specific commands.

        Arguments:
        ----------
        channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).

        """
        try:
            self.r = redis_instance
        except Exception as e:
            print(e)
    def configure(self, redis_channels, **kwargs):
        for c in redis_channels:
            self.r.publish(c,signals.CONFIG + ' ' + str(kwargs))
    def start(self, redis_channels, **kwargs):
        for c in redis_channels:
            self.r.publish(c,signals.START + ' ' + str(kwargs))
    def stop(self, redis_channels, **kwargs):
        for c in redis_channels:
            self.r.publish(c,signals.STOP + ' ' + str(kwargs))
    def get_active_devices(self):
        devices = [key.decode("utf-8") for key in self.r.keys() if key.decode("utf-8").startswith(config.DEV_KEY_PREFIX)]
        devices = [dev.replace(config.DEV_KEY_PREFIX,'') for dev in devices]
        return devices
    def get_device_config(self, device):
        cfg = redis_to_dict(self.r.get(config.DEV_KEY_PREFIX+device))
        return cfg

