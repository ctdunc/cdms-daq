from rejson import Path
import time
from tesdaq.constants import Config, Signals
from tesdaq.query import get_device_state
def configure(redis_instance, device, to_update):
    dev_key = Config.DEV_KEY_PREFIX.value+device

    if not redis_instance.exists(dev_key):
        raise ValueError("Device \"{}\" does not exists in the database.".format(device))
        return 1
    prev_state = get_device_state(redis_instance, device)
    
    for task_type, altered_values in to_update.items():
        if prev_state[task_type]:
            for key, value in altered_values.items():
                prev_state[task_type][key] = value
        else:
            prev_state[task_type] = altered_values
    redis_instance.jsonset(dev_key, ".state", prev_state)
    redis_instance.publish(device, Signals.CONFIG.value +" " + str(list(to_update.keys())))
    return 0

def start(redis_instance, device, task_list):

    return 0

def stop(redis_instance, device, task_list):

    return 0
