from tesdaq.listen import TestListener 
from tesdaq.task import TaskRestriction
from tesdaq.task.serialize import TDEncoder
import rejson
r = rejson.Client(encoder=TDEncoder(), decode_responses=True)

analog_in = TaskRestriction(
        num_tasks=1,
        valid_channels=["Dev1","Chan2"],
        valid_timing=["timing"],
        valid_trigger=["Trigger"],
        min_sample_rate=10,
        max_sample_rate=10000,
        volt_ranges=[(-5,5)],
        sr_is_per_chan=True)
digital_in = TaskRestriction(
        num_tasks=1,
        valid_channels=["Dev2","Chan2"],
        valid_timing=["timixxxxxn"],
        valid_trigger=["Trigegigigiigr"],
        min_sample_rate=10,
        max_sample_rate=10000,
        volt_ranges=[(-5,5)],
        sr_is_per_chan=True)
testlistener = TestListener("test", r, analog_in=analog_in, digital_in=digital_in)
testlistener.wait()
