from tesdaq.constants import Signals, Config
from tesdaq.listen.parameters import TaskState, TaskRestriction
from rejson import Path
import time
import re

class DAQCommander:
    def __init__(
            self,
            redis_instance):
        
        """__init__

        Parameters
        ----------
        redis_instance: redis.Redis
            instance to connect to.
        """
        self.r = redis_instance
    def configure(self, device, to_update, unset_previous=False):
        """configure
        Updates existing task state in Redis.
        Sends CONFIG message to device channel, with list of updated tasks.
        
        :param device:
        :param to_update:
        :param unset_previous:
        """
        # Check device exists
        device_key = Config.DEV_KEY_PREFIX.value+device
        if not self.r.exists(device_key):
            raise ValueError("Device \"{}\" does not appear to exist. Unable to configure.".format(device))
        state = self.get_device_state(device)
        for task_type, altered_values in to_update.items():
            if state[task_type]:
                for key, value in altered_values.items():
                    if unset_previous:
                        delattr(state[task_type], key, value)
                    setattr(state[task_type], key, value)
        for key in state.keys():
            state[key] = state[key].json_repr()
        self.r.jsonset(device_key, Path.rootPath(), state)
        self.r.publish(device, Signals.CONFIG.value+" "+str(list(to_update.keys())))
    def start(self, device, task_list):
        return 0
    def stop(self, device, task_list):
        return 0

    # Getters from RDB.
    def get_existing_devices(self):
        """get_existing_devices
        Gets all existing device names in redis database.
        """
        keys = []
        for key in self.r.keys():
            if key.startswith(Config.DEV_KEY_PREFIX.value):
                keys.append(key.replace(Config.DEV_KEY_PREFIX.value, ''))
        return keys
    def get_device_state(self, device):
        """get_device_state
        Gets state of device as {"task_name": obj} pairs.

        :param device:
        """
        keys = self.r.jsonobjkeys(Config.DEV_KEY_PREFIX.value+device, Path.rootPath())
        paths = [Path("."+k+".state") for k in keys]
        state = self.r.jsonget(Config.DEV_KEY_PREFIX.value+device, *paths)
        restriction = self.get_device_restriction(device)
        for key in keys:
            oldkey = [k for k in list(state.keys()) if key in k][0]
            state[key] = TaskState(**state[oldkey],restriction=restriction[key])
            del state[oldkey]
        return state
    def get_device_restriction(self, device):
        """get_device_restriction
        Gets restriction of device as {"task_name": obj} pairs.

        :param device:
        """
        keys = self.r.jsonobjkeys(Config.DEV_KEY_PREFIX.value+device, Path.rootPath())
        ks = [Path("."+k+".restriction") for k in keys]
        restriction = self.r.jsonget(Config.DEV_KEY_PREFIX.value+device, *ks)
        for key in keys:
            oldkey = [k for k in list(restriction.keys()) if key in k][0]
            restriction[key] = TaskRestriction(**restriction[oldkey])
            del restriction[oldkey]
        return restriction
