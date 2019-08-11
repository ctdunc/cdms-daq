from tesdaq.constants import states, signals, config
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
        self.r.publish(device,signals.CONFIG + ' ' + str(task_dict))
    def start(self, c, **kwargs):
            self.r.publish(c,signals.START + ' ' + str(kwargs))
    def stop(self, c, **kwargs):
            self.r.publish(c,signals.STOP + ' ' + str(kwargs))
    def get_active_devices(self):
        devices = [key.decode("utf-8") for key in self.r.keys() if key.decode("utf-8").startswith(config.DEV_KEY_PREFIX)]
        devices = [dev.replace(config.DEV_KEY_PREFIX,'') for dev in devices]
        return devices
    def get_device_config(self, device):
        cfg = redis_to_dict(self.r.get(config.DEV_KEY_PREFIX+device+config.DEV_STATE_POSTFIX))
        return cfg

