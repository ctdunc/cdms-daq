from listen.daq_listen import DAQListener
import myDAQLibrary as mdl # Support layer for whichever DAQ you want to use

class MyCustomDAQ(DAQListener):

    def __init__(self, arg1, arg2, **kwargs):
        # passes kwargs like redis_host to DAQListener init method
        # handles redis connection and creates callback functions/wait method.
        super(MyCustomDAQ, self).__init__(**kwargs)

        self.__do_something_with_positional_args(arg1, arg2)

    def __do_something_with_positional_args(self, arg1, arg2):
        result = 0
        # do something that affects result
        return result

    def __do_alpha(self, **kwargs):
        # do something
        mdl.change_alpha()
        return 0
    def __do_beta(self, **kwargs):
        """
        do something else, with different arguments
        this is primarily useful if you have two different libraries,
        each of which can be configured independently of the other
        (see listen/ni_6120 for an example of configuring an ni.Task() instance
        as well as a socketio instance, and some save protocol)
        """
        mdl.change_beta()
        return 0
    def configure(self, **kwargs):
        """
        when wait() loop recieves "CONFIG {....}"
        do something with dict elements as keyword arguments
        """

        if "alpha" in kwargs:
            self.__do_alpha(**kwargs["alpha"])
        if "beta" in kwargs:
            self.__do_beta(**kwargs["beta"])
    def start(self):
        """
        do something on "START"
        """
        mdl.start_acquisition()
        return 0

    def stop(self):
        """
        do something on "STOP"
        """
        ok_to_stop = mdl.check_some_stop_condition()
        if ok_to_stop:
            mdl.stop_acquisition()
        else:
            err = mdl.handle_error()
            log_error(err)
        return 0

