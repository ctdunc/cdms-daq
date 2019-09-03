import time
import json
from rejson import Client
import tesdaq.command as c
import tesdaq.query as q
r = Client(decode_responses=True)
d = q.get_existing_devices(r)[0]
c.configure(r, d, {"analog_in":{"channels": ["Dev1"], "sample_rate":11}})
