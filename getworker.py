from tesdaq.command.daq_cmd import DAQCommander
import redis
r = redis.Redis()
cmd = DAQCommander(r)
devs = cmd.get_active_devices()
cfg = cmd.get_device_config(devs[0])
print(cfg)
