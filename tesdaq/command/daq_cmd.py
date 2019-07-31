from ..daq_constants import states, signals
import redis
import time
import re

class DAQCommander:
    def __init__(
            self,
            redis_channels=['def'],
            redis_host='localhost',
            redis_password='',
            redis_port=6379,
            redis_database=0,
            **kwargs):

        """ Convenience class to issue Redis messages to execute specific commands.

        Arguments:
        ----------
        channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).

        """
        self.channels = redis_channels
        try:
            self.r = redis.Redis(
                host=redis_host,
                password=redis_password,
                port=redis_port,
                db=redis_database
                )

        except Exception as e:
            print(e)
    
    def configure(self, **kwargs):
        for c in self.channels:
            self.r.publish(c,signals.CONFIG + ' ' + str(kwargs))
    def start(self, **kwargs):
        for c in self.channels:
            self.r.publish(c,signals.START + ' ' + str(kwargs))
    def stop(self, **kwargs):
        for c in self.channels:
            self.r.publish(c,signals.STOP + ' ' + str(kwargs))
