""" Module containing constants that are used to communicate various
configurable variables existence to the Redis instance/server.

Currently modeled heavily from NI-daqmx,
but avoiding explicitly using their library for cross-compatibility.

If these values are indeed configured, they will be passed to the server as dicts.
If not, they shouldn't render options on the frontend.
"""
DEV_KEY_PREFIX = "_tesdaq.dev."
DEV_RESTRICT_POSTFIX = ".restrict"
DEV_STATE_POSTFIX = ".state"

VOLT = "VOLT"
CURRENT = "AMP"
RESISTANCE = "OHM"

