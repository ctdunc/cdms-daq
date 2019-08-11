import nidaqmx
from tesdaq.listen import DeviceListener
from tesdaq.listen.parameters import 
def task_restrict_from_nidaqmx(devicename):
    ni_dev = nidaqmx.system.device.Device(devicename)
    return 0

class DAQmxListener(DeviceListener):
    def __init__(self,
            identifier,
            redis_instance,
            **kwargs):
        super(DAQmxListener, self).__init__(identifier, redis_instance, **kwargs)

    def configure(self, **kwargs):
        print(self.state) 
    def start(self):
        print("do nothing yet")
    def stop(self):
        print("stop")
