from pymodaq.daq_utils.daq_utils import ThreadCommand, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.daq_utils.parameter import Parameter

class PythonWrapperOfYourInstrument:
    #  TODO Replace this fake class with the import of the real python wrapper of your instrument
    pass


class DAQ_2DViewer_Template(DAQ_Viewer_base):
    """
    """
    params = comon_parameters + [
        ## TODO for your custom plugin
        # elements to be added here as dicts in order to control your custom stage
        ############
    ]

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: PythonWrapperOfYourInstrument = None

        # TODO declare here attributes you want/need to init with a default value

        self.x_axis = None
        self.y_axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        # TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
            self.controller.your_method_to_apply_this_param_change()
        #elif ...

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        raise NotImplemented  # TODO when writing your own plugin remove this line and modify the one below
        self.ini_detector_init(old_controller=controller,
                               new_controller=PythonWrapperOfYourInstrument())

        ## TODO for your custom plugin
        # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
        data_x_axis = self.controller.your_method_to_get_the_x_axis()  # if possible
        self.x_axis = Axis(data=data_x_axis, label='', units='')

        # get the y_axis (you may want to to this also in the commit settings if y_axis may have changed
        data_y_axis = self.controller.your_method_to_get_the_y_axis()  # if possible
        self.y_axis = Axis(data=data_y_axis, label='', units='')

        ## TODO for your custom plugin. Initialize viewers pannel with the future type of data
        self.data_grabed_signal_temp.emit([DataFromPlugins(name='Mock1', data=["2D numpy array"],
                                                           dim='Data2D', labels=['dat0'],
                                                           x_axis=self.x_axis,
                                                           y_axis=self.y_axis), ])

        # note: you could either emit the x_axis, y_axis once (or a given place in the code) using self.emit_x_axis()
        # and self.emit_y_axis() as shown above. Or emit it at every grab filling it the x_axis and y_axis keys of
        # DataFromPlugins)

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin

        ##synchrone version (blocking function)
        data_tot = self.controller.your_method_to_start_a_grab_snap()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                      dim='Data2D', labels=['dat0'])])
        # note: you could either emit the x_axis once (or a given place in the code) using self.emit_x_axis() as shown
        # above. Or emit it at every grab filling it the x_axis key of DataFromPlugins, not shown here)

        ##asynchrone version (non-blocking function with callback)
        self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                      dim='Data2D', labels=['dat0'])])

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
