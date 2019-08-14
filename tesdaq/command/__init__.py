from tesdaq.constants import Signals, Config
from tesdaq.listen.parameters import redis_to_dict
import redis
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
        task_dict:
            dict containing parameters, tasks to be updated. 
            e.g. change sample rate of task "analog_in" to 100, add channel "Dev1/di8" to "digital_in":
            {
                "analog_in": {
                    "sample_rate", 100
                }, 
                "digital_in": {
                "channels":["Dev1/di8"]
                }
            }
        Returns
        -------
        """
        try:
            self.r = redis_instance
        except Exception as e:
            print(e)
    def configure(self, device, task_dict, unset_previous=False):
        """configure

        Parameters
        ----------
        device: str
            device key to update.
        task_dict: dict
            dict containing parameters, tasks to be updated. 
            e.g. to change sample rate of task "analog_in" to 100, add channel "Dev1/di8" to "digital_in":
            {
                "analog_in": {
                    "sample_rate", 100
                }, 
                "digital_in": {
                "channels":["Dev1/di8"]
                }
            }
        unset_previous: bool, optional
            Determines whether previously set values will be reset to zero before instantiation, or if values will be added.
        """
        task_dict['unset_previous']=unset_previous
        self.r.publish(device,Signals.CONFIG.value + ' ' + str(task_dict))
    def start(self, c, **kwargs):
            self.r.publish(c,Signals.START.value + ' ' + str(kwargs))
    def stop(self, c, **kwargs):
            self.r.publish(c,Signals.STOP.value + ' ' + str(kwargs))
    def get_active_devices(self):
        devices = [key.decode("utf-8") for key in self.r.keys() if key.decode("utf-8").startswith(Config.DEV_KEY_PREFIX.value)]
        devices = [dev.replace(Config.DEV_KEY_PREFIX.value,'') for dev in devices]
        devices = [dev.replace(Config.DEV_STATE_POSTFIX.value,'') for dev in devices if dev.endswith(Config.DEV_STATE_POSTFIX.value)]
        return devices
    def get_device_state(self, device):
        state = self.r.get(Config.DEV_KEY_PREFIX.value+device+Config.DEV_STATE_POSTFIX.value)
        state = redis_to_dict(state)
        return state
    def get_device_restriction(self, device):
        restrict = self.r.get(Config.DEV_KEY_PREFIX.value+device+Config.DEV_RESTRICT_POSTFIX.value)
        restrict = redis_to_dict(restrict)
        return restrict
