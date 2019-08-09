name = "listen"
import time
# from redis.exceptions import ConnectionError
from ..constants import states, signals, config
from parameters import TaskState, DeviceRestriction

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

        self.id = config.DEV_KEY_PREFIX+identifier
        self.state_key = self.id+config.DEV_STATE_POSTFIX
        self.restrict_key = self.id+config.DEV_RESTRICT_POSTFIX

        self.r = redis_instance
        val = self.r.get(self.state_key)

        if val:
            raise ValueError("A listener with id \"{}\" already exists. Please use a different id, or stop that worker, and unset the redis key.".format(self.id))
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(identifier)
    
        self.tasks = {}
        for task_type, restriction in kwargs.items():
            self.tasks[task_type] = TaskState(restriction)

        # Check if key is reserved
        
