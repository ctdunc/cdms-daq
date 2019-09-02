import time
import json
from rejson import Client
import tesdaq.query as t
r = Client(decode_responses=True)
d = t.get_existing_devices(r)[0]
