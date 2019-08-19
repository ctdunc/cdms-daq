import time
from tesdaq.command import DAQCommander
import redis
r = redis.Redis()
cmd = DAQCommander(r)
devs = cmd.get_active_devices()
print(devs[0])
d = devs[0]
rest = cmd.get_device_restriction(d)
state = cmd.get_device_state(d)

