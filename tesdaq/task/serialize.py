import json
from collections import namedtuple
from tesdaq.task import TaskState, TaskRestriction
class TDEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, TaskState):
            return {
                    'channels': obj.channels,
                    'sample_rate': obj.sample_rate,
                    'trigger_mode': obj.trigger_mode,
                    'timing_mode':  obj.timing_mode
                    }
        return json.JSONEncoder.default(self, obj)

class TDDecoder(json.JSONDecoder):

    def default(self, obj):

        return json.JSONDecoder.default(self, obj)
