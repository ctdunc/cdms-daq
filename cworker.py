from tesdaq.listen import DeviceListener
from tesdaq.types import TaskRestriction

import rejson
r = rejson.Client()

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
testlistener = DeviceListener("test_222", r, analog_in=analog_in, digital_in=digital_in)
testlistener.wait()
