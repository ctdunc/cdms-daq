from tesdaq.listen import TestListener
import redis
r = redis.Redis()
test_listener = TestListener(
        "test", 
        {
        "cfg_analog_input":{
            "channels": ["Dev1/ai0"],
            "max_sample_rate": 100000,
            "min_sample_rate": 100,
            "sr_is_per_chan": False,
            "trigger_opts": []
            }
        },
        r)
test_listener.wait() #
