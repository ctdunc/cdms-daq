from tesdaq.listen.ni import DAQmxListener
from tesdaq.listen.parameters import TaskTypeRestriction, TaskState
import redis
r = redis.Redis()

a_rest = TaskTypeRestriction(
        num_tasks=2,
        valid_channels=["Dev1/ai0","Dev1/ai1","Dev1/ai2"],
        valid_timing=["triggered", "continuous"],
        max_sample_rate=100000,
        min_sample_rate=10,
        sr_is_per_chan=False
        )

d_rest = TaskTypeRestriction(
        num_tasks=2,
        valid_channels=["Dev1/di0","Dev1/di1","Dev1/di2"],
        valid_timing=["triggered", "continuous"],
        max_sample_rate=1000,
        min_sample_rate=10,
        sr_is_per_chan=True
        )

testlistener = DAQmxListener("test", r, ai_in=a_rest, di_in=d_rest)
testlistener.wait()
