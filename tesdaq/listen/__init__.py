name = "listen"
import time
from redis.exceptions import ConnectionError
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
        self.state_key = self.id+Config.DEV_STATE_POSTFIX.value
        self.restrict_key = self.id+Config.DEV_RESTRICT_POSTFIX.value

        self.r = redis_instance

        # Check if key is reserved
        state_val = self.r.get(self.state_key)
        restrict_val = self.r.get(self.restrict_key)

        if state_val:
            raise ValueError("A listener with id \"{}\" already exists. Please use a different id, or stop that worker, and unset the redis keys.".format(self.id))
        elif restrict_val:
            print("A restriction for listener \"{}\" exists, but no state has been set. Restriction will be reset.".format(self.id))

        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(identifier)
         
        self.__state = {}
        self.__restrictions = {}
        for task_type, restriction in kwargs.items():
            self.__state[task_type] = TaskState(restriction)
            self.__restrictions[task_type] = restriction
        self.r.set(self.state_key, str(self.state))
        self.r.set(self.restrict_key, str(self.restrictions))
    @property
    def state(self):
        rdict = {}
        for key, val in self.__state.items():
            rdict[key] = val.current_state
        return rdict
    @property
    def restrictions(self):
        rdict = {}
        for key, val in self.__restrictions.items():
            rdict[key] = dict(val._asdict())
        return rdict
    def __update_active_state(self, task_type, signal):
        """update_active_state

        Parameters
        ----------
        task_type: str
            Type of task whose state is to be updated.
        signal:
            Signal which was recieved.
        Returns
        -------
        """
        if signal == Signals.START:
            self.__state[task_type].is_active = True
        if signal == Signals.STOP:
            self.__state[task_type].is_active = True
        self.r.set(self.state_key, self.state)
    def __config_active_state(self, to_configure):
        """__config_active_state

        Parameters
        ----------
        to_configure: dict
            Type of class, with parameters to be reset. Whether specific assets should be reset.

        Returns
        -------
        """
        should_delete = to_configure['unset_previous']
        del to_configure['unset_previous']
        for task_type, to_update in to_configure.items():
            # Check for valid task type
            if self.__state[task_type]:
                for key, value in to_update.items():
                    if should_delete:
                        delattr(self.__state[task_type], key)
                    setattr(self.__state[task_type], key, value)
            else:
                raise ValueError("Invalid Task Type \"{}\"".format(task_type))
    def __update_rdb(self):
        redis_state = redis_to_dict(self.r.get(self.state_key))
        if redis_state != self.state:
            self.r.set(self.state_key, str(self.state))
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
            self.__update_rdb()
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
                    self.__update_run_state(Signals.START.value)
                if command.startswith(Signals.CONFIG.value):
                    self.configure(**passed_args)
                    self.__config_active_state(passed_args)
                if command.startswith(Signals.STOP.value):
                    self.__update_run_state(Signals.STOP.value)
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
