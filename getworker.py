from tesdaq.command import DAQCommander
import redis
r = redis.Redis()
cmd = DAQCommander(r)
devs = cmd.get_active_devices()
print(devs[0])
cmd.configure(devs[0])
