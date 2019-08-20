name = "listen"
import time
import re
import ast
from redis.exceptions import ConnectionError
from rejson import Path
from tesdaq.constants import Signals, Config
from tesdaq.listen.parameters import TaskState

class DeviceListener:
    def __init__(
            self,
            identifier,
            redis_instance,
            **kwargs):
        """__init__

        Parameters
        ----------
        identifier: str
            Unique string used to get and set values in redis database.
        redis_instance: redis.Redis
            Redis instance to connect
        **kwargs:
            key, value pairs that correspond to task types and restrictions (e.g. analog_input=DeviceRestriction(...))
        Returns
        -------
        """

        self.id = Config.DEV_KEY_PREFIX.value+identifier

        self.r = redis_instance

        # Check if key is reserved
        rdb_val = self.r.jsonget(self.id) 

        if rdb_val:
            raise ValueError("A listener with id \"{}\" already exists. Please use a different id, or stop that worker, and unset the redis keys.".format(self.id))

        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(identifier)

        self.__state = {}
        for task_type, restriction in kwargs.items():
            self.__state[task_type] = TaskState(restriction)
        self.r.jsonset(self.id, Path.rootPath(), self.state)

    @property
    def state(self):
        """state
        Returns
        -------
        Representation of state as JSON serializable object. 
        There's basically no other reason to access it as the TaskState object outside of this class.
        """
        return dict(map(lambda entry: (entry[0], entry[1].json_repr()), self.__state.items()))

    def update_state(self, tasks_to_configure):
        """update_state
        Updates local state.

        Parameters
        ----------
        tasks_to_configure: dict with following structure:
            {"task_type": {
                "parameter_to_change_1": [new, value],
                "other_parameter":      "new_value"
                }
            }
        Returns
        -------
        status: bool
            Returns true if changes have been made.
        """
        status = False
        should_reset = tasks_to_configure['unset_previous']
        del tasks_to_configure['unset_previous']
        for task_type, to_update in tasks_to_configure.items():
            # Check for existing task_type. If not, raise an error.
            if self.__state[task_type]:
                for key, value in to_update.items():
                    if should_reset:
                        delattr(self.__state[task_type]['state'], key)
                    setattr(self.__state[task_type]['state'], key, value)
            else:
                raise ValueError("Invalid Task Name \"{}\"".format(task_type))
    
    def update_rdb(self):
        """update_rdb
        Updates redis database with new state.
        """

    def configure(self, **kwargs):
        """configure
        executed when Signals.CONFIG is recieved in wait() loop.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self, **kwargs):
        """start
        executed when Signals.START is recieved in wait() loop.
        Inheriting classes should be sure long-polling actions taken in this function execute **asynchronously**, otherwise task state will fail to update.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement start()".format(type(self).__name__))
    def stop(self, **kwargs):
        """stop
        executed when Signals.STOP is recieved in wait() loop.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement stop()".format(type(self).__name__))
    def wait(self):
        while True:
            message = self.pubsub.get_message()
            if message:
                command=message['data']
                try:
                    command = str(command.decode("utf-8"))
                except AttributeError:
                    command = str(command)
                prefix = re.search('([^\s]+)', command).group(0)
                task_str = command.replace(prefix, '').strip()
                task_types = []
                if task_str:
                    task_types = ast.literal_eval(task_str)
                if prefix==Signals.CONFIG.value:
                    self.update_state_from_redis(**task_types)
                    self.config(**task_types)
                if prefix==Signals.STOP.value:
                    self.stop(**task_types)
                    self.update_run_states(**task_types, prefix)
                if prefix==Signals.START.value:
                    self.start(**task_types)
                    self.update_run_states(**task_types, prefix)
            time.sleep(.1)


class TestListener(DeviceListener):
    def __init__(self, identifier,  redis_instance, **kwargs):
        super(TestListener, self).__init__(identifier, redis_instance, **kwargs)
    def configure(self, **kwargs):
        print(kwargs)
    def start(self, **kwargs):
        print(kwargs)
    def stop(self, **kwargs):
        print(kwargs)
