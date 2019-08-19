name = "listen"
import time
from redis.exceptions import ConnectionError
from rejson import Path
from tesdaq.constants import Signals, Config
from tesdaq.listen.parameters import TaskState, redis_to_dict

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

        self.__device = {}
        for task_type, restriction in kwargs.items():
            self.__device[task_type] = TaskState(restriction)
        self.r.jsonset(self.id, Path.rootPath(), self.__device.json_repr())

    def diff_update_rdb(self, tasks_to_configure):
        """diff_update_rdb

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
        """
        should_reset = tasks_to_configure['unset_previous']
        del tasks_to_configure['unset_previous']
        for task_type, to_update in tasks_to_configure.items():
            if self.__device[task_type]:
                for key, value in to_update.items():
                    if should_reset:
                        delattr(self.__device[task_type]['state'], key)
                    setattr(self.__device[task_type]['state'], key, value)
            else:
                raise ValueError("Invalid Task Name \"{}\"".format(task_type))
        


    def get_rdb(self):
        status = 0

        return status
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
            ## UPDATE
            message = self.pubsub.get_message()
            if message:
                command=message['data']
                try:
                    command = str(command.decode("utf-8"))
                except AttributeError:
                    command = str(command)
                passed_args = redis_to_dict(command)
                if command.startswith(Signals.START.value):
                    self.start(**passed_args)
                    # UPDATE
                if command.startswith(Signals.CONFIG.value):
                    previous_state = self.__state
                    should_configure = False
                    try:
                        self.__config_active_state(passed_args)
                        should_configure = True
                    except ValueError as e:
                        self.__state = previous_state
                        raise e
                    if should_configure:
                        self.configure()
                if command.startswith(Signals.STOP.value):
                    print(stop)
                    #UPDATE
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
