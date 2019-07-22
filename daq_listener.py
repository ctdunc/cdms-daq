"""TODO:
    finish dosctring
"""

import redis
import time
import re
import ast

to_dict = lambda st: ast.literal_eval(re.search('({.+})', st).group(0))
# Defines some states
WAIT = 0
RUN = 1
REDIS_FAILURE = -1

# Define commands passed from redis
CMD_START = "START"
CMD_STOP = "STOP"
CMD_CONFIG = "CONFIG"

class DAQListener:
    def __init__(
            self,
            channels,
            redis_host='localhost',
            redis_password='',
            redis_port=6379,
            redis_database=0):

        """ Abstraction for listening to redis messages to execute DAQ commands

        Arguments:
        ----------
        channels:   Array of strings which redis will subscribe to as channels. (Must be an array!)
        redis_host: Host to which redis connects (e.g. 'localhost')
        redis_port: Port which redis should use to connect (by default is 6379)
        redis_database: Redis DB to be used (default, 0).

        """
        r = redis.Redis(
            host=redis_host,
            password=redis_password,
            port=redis_port,
            db=redis_database
            )
        try:
            self.pubsub = r.pubsub()
            for c in channels:
                self.pubsub.subscribe(c)
            self.STATE = WAIT

        # TODO: More specific exception here
        except Exception as e:
            self.STATE = REDIS_FAILURE
            print(e)

    def configure(self):
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self):
        raise NotImplementedError("class {} must implement start()".format(type(self).__name__))
    def stop(self):
        raise NotImplementedError("class {} must implement stop()".format(type(self).__name__))

    def wait(self):
        while self.STATE == WAIT:
            message = self.pubsub.get_message()
            if message:
                command = message['data']

                try:
                    command = str(command.decode("utf-8"))
                except AttributeError as e:
                    command = str(command)

                if command == CMD_START:
                    self.start()
                if command.startswith(CMD_CONFIG):
                    parameters = to_dict(command)
                    self.configure(**parameters)
                if command == CMD_STOP:
                    self.stop()
            time.sleep(1)
