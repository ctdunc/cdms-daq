name = "listen"
import time
import re
import ast
from redis.exceptions import ConnectionError
from rejson import Path
from tesdaq.constants import Signals, Config
from tesdaq.task import TaskState
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
            key, value pairs that correspond to task types and constraint objects. 
            Must be json serializable by encoder used by redis_instance.

        """
        self.chan = identifier
        self.id = Config.DEV_KEY_PREFIX.value+identifier

        self.r = redis_instance

        # Check if key is reserved
        rdb_val = self.r.jsonget(self.id) 
        if rdb_val:
            raise ValueError("A listener with id \"{}\" already exists. Please use a different id, or stop that worker, and unset the redis keys.".format(self.id))

        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(identifier)

        self.state = {}
        res = {}
        self.r.jsonset(self.id, Path.rootPath(), {})
        for task_type, restriction in kwargs.items():
            self.state[task_type] = TaskState(restriction)
            res[task_type] = restriction._asdict()
        self.r.jsonset(self.id,".restriction", res)
        self.r.jsonset(self.id,".state", self.state)
    
    def _validate_redis_changes(self, to_update):
        for t in to_update:
            task = self.r.jsonget(self.id)['state'][t]
            for key, value in task.items():
                if value != getattr(self.state[t],key):
                    try:
                        setattr(self.state[t], key, value)
                    except ValueError as e:
                        print(str(e))
            self.r.jsonset(self.id, ".state", self.state)
        return 0
    def configure(self, **kwargs):
        """configure
        executed when Signals.CONFIG is recieved in wait() loop.
        This should bridge the state of the DAQ itself to the database.

        Parameters
        ----------
        **kwargs:
            Passed as JSON-formatted string from Redis, and expanded in wait loop.
        """
        raise NotImplementedError("class {} must implement configure()".format(type(self).__name__))
    def start(self, **kwargs):
        """start
        executed when Signals.START is recieved in wait() loop.
        Inheriting classes should be sure long-polling actions taken in this function execute **asynchronously**, 
        otherwise task state will fail to update on subsequent changes until those actions are completed.

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
                    self._validate_redis_changes(task_types)
                    self.configure(task_types)
                if prefix==Signals.STOP.value:
                    self.stop(*task_types)
                if prefix==Signals.START.value:
                    self.start(*task_types)
            time.sleep(.1)


class TestListener(DeviceListener):
    def __init__(self, identifier,  redis_instance, **kwargs):
        super(TestListener, self).__init__(identifier, redis_instance, **kwargs)
    def configure(self, task_types):
        print(task_types)
    def start(self, **kwargs):
        print(kwargs)
    def stop(self, **kwargs):
        print(kwargs)
