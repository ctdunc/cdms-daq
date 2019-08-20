import time
from tesdaq.command import DAQCommander
from rejson import Client
r = Client(decode_responses=True)
cmd = DAQCommander(r)
devs = cmd.get_existing_devices()
d = devs[0]
res = cmd.get_device_restriction(d)
sta = cmd.get_device_state(d)
print(res)
print(sta)
cmd.configure(d, {"analog_in":{"sample_rate":100, "channels":["Dev1", "Chan2"]}, "digital_in":{"sample_rate":200}})
sta = cmd.get_device_state(d)
print(sta)
