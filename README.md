![logo](./doc/logo.png)
# tesdaq
## Introduction
### What is this?
This repository contains code used by the Pyle Group at UC Berkeley to continuously acquire voltage measurements from an NI6120 digitizer. 
Specifically, it is designed to facilitate unifying DAQ systems and devices over many computers and even experiment locations, as well as provide a simple backend implementation to our web-based pulseviewer, [adcscope](https://github.com/ucbpylegroup/adcscope).
It should work for many other DAQ systems, however, and as more devices are added, this document will be updated accordingly.

### Why does this exist?
Isn't this just a [celery](http://www.celeryproject.org/) or [rq](http://python-rq.org/) clone? Those are way more fleshed out, so wouldn't it make more sense to use those?
Well yes, but actually no.

This project arose from my (Connor) frustration with two features common to nearly every task-management library in python.
* Difficulty in specifying _which_ worker should execute a task
* Poor management of asynchronous subtasks (specifically with [nidaqmx](https://github.com/ni/nidaqmx-python) tasks).

These features make a lot of sense in the context of the applications they're actually designed to handle, but aren't great for Data Acquisition. 
Most celery tasks for instance, are centered around making potentially long-running API calls, which still return values directly to the user who sent the request through the same backend the request was sent through ([this](https://www.fullstackpython.com/celery.html) is a good explainer).

Data Acquisition, however, can potentially run forever (until the user stops it, or the task runs out of memory), and needs to return Data to the user _as it is acquired_ if any semblance of real-time visualization is to be achieved.

This library is an effort to implement a basic publish-subscribe framework in Redis that allows scalable DAQ pipelines without requiring tons of conceptual overhead in implementation.
It also adds some compatibility layers between various DAQ libraries (such as nidaqmx), and redis pub-sub, and as I use more devices, I will add more classes.

## Getting Started
This project is still under development, and may cause errors if you attempt to deploy it immediately into a production environment without first testing it.

### Requirements
In order to develop or test this project for yourself, ensure that you have a working version of python 3.6+ installed on your computer, as well as a running [redis server](https://redis.io/), which is the required backend for this program. 

There are zero guarantees that this will work on either Windows or MacOS. You'll probably have better luck with Mac, but best results will come from using [CentOS](https://centos.org)-based Linux distributions. This application is developed on [Arch](https://www.archlinux.org/), and [Scientific Linux 7](https://www.scientificlinux.org/). 
Device-specific development is done only on Scientific Linux 7.

To use this library, simply open a virtual environment using
```bash
[user@computer]$ python -m venv env
[user@computer]$ source env/bin/activate
[user@computer]$ pip install --upgrade tesdaq
```
Then, you can import modules in the following manner:
```python
from tesdaq.listen.daq_listen import DAQListener
from tesdaq.listen.ni_6120 import NI6120

from tesdaq.command.daq_cmd import DAQCommander
```

Plans exist to shorten this import structure.

### Testing
tesdaq by default does not assume which machines any programs are running on. Rather, it uses a [pub/sub](https://redis.io/topics/pubsub) structure to issue/receive commands and data. Thus, a minimal working example requires a _commander_ and a _listener_. 
The simplest case is a program that implements a single listener on a default channel, and prints a message when a signal is received.

Such a listener might look like this:
```python
# ./sample_listener.py
from tesdaq.listen.daq_listen import TestListener

test_listener = TestListener() # if your redis parameters are different (port, db etc) change them here
test_listener.wait() # sends the listener into a loop where it waits for signals
```

Similarly, we create a new `DAQCommander`, which is capable of issuing messages to the listener, which will act upon their reception.
Let's create a new commander that issues a `START` command, waits for ten seconds, and then issues a `STOP` command.

```python
# ./sample_commander.py
from tesdaq.command.daq_cmd import DAQCommander
import time

test_commander = DAQCommander() # again, make sure you are connected to your redis instance
test_commander.start(some_sample_keyword_arg={"this is a sample":[1,2,3,4]})
time.sleep(10)
test_commander.stop(shutdown_gracefully=True)
```

Now, in two separate terminals, (or [tmux](https://github.com/tmux/tmux/wiki) if you're feeling brave), start `sample_listener`, and `sample_commander` in that order, and watch as `sample_commander`'s keyword arguments appear with the correct message on `sample_listener`'s output!

## Next Steps
The previous example is generally too simple for the needs of any experiment, however. 
It is also very difficult to add a compatibility layer for _every single DAQ system_ in existence, which is why the chances that you will need to write your own class to control your device. 
### Device-Specific Classes
Since most devices have different libraries/functionality, it's hard to create a one-size fits all template that will perfectly allow you to control every single device.
That is why the `DAQListener` class exists! `DAQListener` defines one function, `wait()`, which creates a loop that polls whatever Redis instance and channels are passed in upon instantiation once per second (I plan on adding the opportunity to configure this poll rate in the very near future).
Upon receiving these signals, it executes either the `configure()`, `start()`, or `stop()` methods, which are not defined in advance, and must be defined by any class inheriting from `DAQListener`.

For example: the `TestListener` example from above simply takes this structure, and upon receiving each signal, prints whatever keyword arguments are sent to each function.
```python
# listen/daq_listen.py
class TestListener(DAQListener):
    def __init__(self, **kwargs):
        super(TestListener, self).__init__(**kwargs)

    def configure(self, **kwargs):
        print("RECIEVED MESSAGE CONFIG", kwargs)
        return 0
    def start(self, **kwargs):
        print("RECIEVED MESSAGE START", kwargs)
        return 0
    def stop(self, **kwargs):
        print("RECIEVED MESSAGE STOP", kwargs)
        return 0
```

A more fleshed out example of how this might look in practice can be found in this [custom class template](./doc/examples/custom_class_template.py). Note that this is pseudocode, and will definitely not work if you try to implement it as-is (it assumes the existence of some fake DAQ library as a standin for whichever you choose to use).

#### My Device Doesn't Support Python (or Python is too slow)!
Not to worry! Redis has support for [basically all the programming languages](https://redis.io/clients). If there's a client for Scheme, there's probably a client for your language. 
As devices are added, it's only a matter of time before one doesn't support python-based control, at which point, classes and documentation will be added to a list below.

It should still be somewhat straightforward to implement something if you need it _right away_. The basic idea is that for any programming language, you spin up some loop `wait()`, which polls the redis database repeatedly until a signal is received, at which point it should handle the signal by some if statement. If you want to use the DAQCommander class to handle your control, those signals would be anything that starts with "CONFIG", "START" or "STOP", and takes in json-like objects.

There are however, **gotchas**. Most of the production-level code in this repository executes _asynchronously_ from the wait loop (specifically [ni_6120](./listen/ni_6120.py) uses [nidaqmx](https://github.com/ni/nidaqmx-python), which executes `tasks` asynchronously, and uses DMA to write to disk).
If you write code that executes _synchronously_  with your `wait()` loop, be sure that each method that can be called from the wait loop remembers to check the database periodically to see if new signals (i.e. `STOP`) have been issued, and is handled accordingly.

A basic (pythonic, but gets the point across) example might be

```python
... some other class stuff here ...
def wait(self): 
	while self.STATE == states.WAIT:
            message = self.pubsub.get_message()
            if message:
                command = message['data']
                passed_args = _to_dict(command) #_to_dict() is defined in daq_listener. Converts JSON object to dict.
                if command.startswith(signals.START):
                    self.start(**passed_args) # start is now synchronous
                if command.startswith(signals.CONFIG):
                    self.configure(**passed_args)
                if command.startswith(signals.STOP):
                    self.stop(**passed_args)

def start(self, **kwargs):
	running = True
	while running:
		do_something_with_kwargs(kwargs)

		message = self.pubsub.get_message()
		if message:
		command = message['data']
		if command.startswith(signals.STOP):
			stop_args = _to_dict(command)
			running = False
		else:
			continue
	self.stop(stop_args)
... potentially more class stuff here ...
```

If you do add any classes/devices to be compatible with this library, be sure to [submit a pull request](https://github.com/ucbpylegroup/tesdaq/pulls) so that others can use your code!

### Deployment
More to come on this soon, but the basic idea is that on each machine where you have a DAQ, you create a script similar to the one from the [testing](#Testing) example, and a [systemd unit file](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) that starts the `wait()` loop on each boot, and stops it before shutdown.
Alternately, you can just run the program from the command line, but that's less efficient and requires you to SSH into the potentially very remote DAQ a lot and creates more overhead.

With some worker running remotely, it is easy to call it from some central command server, for instance a WSGI instance running on apache (my preferred implementation uses [flask](http://flask.pocoo.org/)).
You can then instantly hook the control into a form on a website somewhere, and have browser-based control over all of your devices!

A small sample might be
```python
from flask import Flask, render_template
from tesdaq.command.daq_cmd import DAQCommander

app = Flask(__name__, static_folder='./static/folder', template_folder='./template')

daqctl_for_spec_dev = DAQCommander(redis_channels=["specific_device"]) # use appropriate redis arguments here

@app.route("/")
def render():
	return render_template("index.html")

@app.route("/config_start_form")
def config(json):
	# expands form JSON as keword args
	daqctl.configure(**json)

	return 0

if __name__ == '__main__':
	app.run()
```


