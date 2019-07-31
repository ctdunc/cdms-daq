""" Module containing constants that are used to communicate various
configurable variables existence to the Redis instance/server.

Currently modeled heavily from NI-daqmx,
but avoiding explicitly using their library for cross-compatibility.

If these values are indeed configured, they will be passed to the server as dicts.
If not, they shouldn't render options on the frontend.
"""

# Allowable Channels
ANALOG_IN = "cfg_ai_chans"
ANALOG_OUT = "cfg_ao_chans"

DIGITAL_IN = "cfg_di_chans"
DIGITAL_OUT = "cfg_do_chans"


# Acquisition parameters configurable from front end
# Tells server whether functions are defined for the device in question.
CHAN_CFG = [
    "cfg_analog_input",
    "cfg_digital_input",
    "cfg_analog_output",
    "cfg_digital_output"
]


# Units
VOLT = "VOLT"
CURRENT = "AMP"
RESISTANCE = "OHM"

