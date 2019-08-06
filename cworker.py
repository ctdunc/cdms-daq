from tesdaq.listen import TestListener
import redis
r = redis.Redis()
test_listener = TestListener(
        "test", 
        {
        "cfg_analog_input":{
        "channels": ["Dev1/ai0", "Dev1/ai1", "Dev1/ai2"],
            "max_sample_rate": 100000,
            "min_sample_rate": 100,
            "sr_is_per_chan": False,
            "trigger_opts": []
            },
        "cfg_digital_input":{
        "channels": ["Dev1/di0", "Dev1/di1", "Dev1/di2"],
            "max_sample_rate": 100000,
            "min_sample_rate": 100,
            "sr_is_per_chan": False,
            "trigger_opts": []
            }
        },
        r)
test_listener.wait() #
