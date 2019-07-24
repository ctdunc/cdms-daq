![logo](./logo.png)
# tesdaq
This repository contains code used by the Pyle Group at UC Berkeley to continuously acquire voltage measurements from an NI6120 digitizer. 
Specifically, it is designed to facilitate unifying DAQ systems and devices over many computers and even experiment locations, as well as provide a simple backend implementation to our web-based pulseviewer, [adcscope](https://github.com/ucbpylegroup/adcscope).
It should work for many other DAQ systems, however, and as more devices are added, this document will be updated accordingly.

# Getting Started
## Introduction
This project is still under development, and may cause errors if you attempt to deploy it immediately into a production environment without first testing it.

### Requirements
In order to develop or test this project for yourself, ensure that you have a working version of python 3.6+ installed on your computer, as well as a running [redis server](https://redis.io/), which is the required backend for this program. 

With these requirements fulfilled, simply clone this repository using 
```
git clone https://github.com/ucbpylegroup/tesdaq
```
create and activate a virtual environment using
```
python -m venv env
source env/bin/activate
```
and, install any dependencies required by the package into your new virtual environment using
```
pip install -r pydeps.txt
```

### Testing
tesdaq by default does not assume which machines any programs are running on. Rather, it uses a [pub/sub](https://redis.io/topics/pubsub) structure to issue/recieve commands and data. Thus, a minimal working example requires a _commander_ and a _listener_. 
The simplest case is a program that implements a single listener on a default channel, and prints a message when a signal is recieved.

Such a listener might look like this:
```python
# ./sample_listener.py
from listen.daq_listen import TestListener

test_listener = TestListener() # if your redis parameters are different (port, db etc) change them here
test_listener.wait() # sends the listener into a loop where it waits for signals
```

Similarly, we create a new `DAQCommander`, which is capable of issuing messages to the listener, which will act upon their reception.
Let's create a new commander that issues a `START` command, waits for ten seconds, and then issues a `STOP` command.

```python
# ./sample_commander.py
from command.daq_cmd import DAQCommander
import time

test_commander = DAQCommander() # again, make sure you are connected to your redis instance
test_commander.start(some_sample_keyword_arg={"this is a sample":[1,2,3,4]})
time.sleep(10)
test_commander.stop(shutdown_gracefully=True)
```

Now, in two separate terminals, (or [tmux](https://github.com/tmux/tmux/wiki) if you're feeling brave), start `sample_listener`, and `sample_commander` in that order, and watch as `sample_commander`'s keyword arguments appear with the correct message on `sample_listener`'s output!

## Next Steps
Coming soon...
### Device-Specific Classes


### Deployment


# Development
