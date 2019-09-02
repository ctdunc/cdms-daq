from tesdaq.constants import Signals, Config
from tesdaq.task import TaskState, TaskRestriction
from rejson import Path
import time

def get_existing_devices(redis_instance, restrictions=False, states=False):
    if restrictions or states:
        keys = {} 
    else:
        keys = []
    for key in redis_instance.keys():
        if key.startswith(Config.DEV_KEY_PREFIX.value):
            stripped_key = key.replace(Config.DEV_KEY_PREFIX.value,'')
            if restrictions or states:
                keys[stripped_key] = {}
                if restrictions:
                    keys[stripped_key]['restriction'] = get_device_restriction(redis_instance, stripped_key)
                if states:
                    keys[stripped_key]['state'] = get_device_state(redis_instance, stripped_key)
            else:
                keys.append(stripped_key)
    return keys

def get_device_state(redis_instance, device, path_string=None):
    if path_string is not None:
        path_string = '.'+path_string
    else:
        path_string = ''
    state = redis_instance.jsonget(Config.DEV_KEY_PREFIX.value+device,  ".state"+path_string)
    return state

def get_device_restriction(redis_instance, device, path_string=None):
    if path_string is not None:
        path_string = '.'+path_string
    else:
        path_string = ''
    restriction = redis_instance.jsonget(Config.DEV_KEY_PREFIX.value+device,  ".restriction"+path_string)
    return restriction 

def get_task_type(redis_instance, device, task_type):
    returned_tasks = {}
    if isinstance(task_type, str):
        task_type = [task_type]
    for task in task_type:
        returned_tasks[task] = {}
        restriction = get_device_restriction(redis_instance, device, path_string=task)
        state = get_device_state(redis_instance, device, path_string=task)
        returned_tasks[task]['restriction'] = restriction
        returned_tasks[task]['state'] = state
    return returned_tasks
