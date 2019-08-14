from enum import Enum

name = "constants"

class Config(Enum):
    DEV_KEY_PREFIX = "_tesdaq.dev."
    DEV_RESTRICT_POSTFIX = ".restrict"
    DEV_STATE_POSTFIX = ".state"


class Signals(Enum):
    START = "tesdaq.START"
    STOP = "tesdaq.STOP"
    CONFIG = "tesdaq.CONFIG"

