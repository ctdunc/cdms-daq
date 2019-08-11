import time
from tesdaq.command import DAQCommander
import redis
r = redis.Redis()
cmd = DAQCommander(r)
devs = cmd.get_active_devices()
print(devs[0])
d = devs[0]
cfg = cmd.get_device_config(d)
cmd.configure(devs[0], {"ai_in":{"channels":["Dev1/ai1"]}}, unset_previous=True)
time.sleep(0.5)
print(cmd.get_device_config(d))
cmd.configure(d, {"ai_in":{"channels":["Dev1/ai0"]}})
time.sleep(0.5)
print(cmd.get_device_config(d))
cmd.configure(d, {"ai_in":{"channels":["Dev1/ai0"]}}, unset_previous=True)
time.sleep(0.5)
print(cmd.get_device_config(d))
