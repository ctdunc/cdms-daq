from rejson import Path
import time

def configure(redis_instance, device, to_update, unset_previous=False):
    dev_key = Config.DEV_KEY_PREFIX.value+device

    if not redis_instance.exists(dev_key):
        raise ValueError("Device \"{}\" does not exists in the database.".format(device))
        return 1
    prev_state = get_device_state(redis_instance, device)
    
    for task_type, altered_values in to_update.items():
        if prev_state[task_type]:
            for key, value in altered_values.items():
                if unset_previous:
                    delattr(prev_state[task_type], key)
                setattr(state[task_type], key, value)
    return 0

def start(redis_instance, device, task_list):

    return 0

def stop(redis_instance, device, task_list):

    return 0
