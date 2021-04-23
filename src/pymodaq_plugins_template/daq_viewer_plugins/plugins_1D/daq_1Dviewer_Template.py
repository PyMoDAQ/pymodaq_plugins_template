import numpy as np
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters


class DAQ_1DViewer_Template(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[
        ## TODO for your custom plugin
        # elements to be added here as dicts in order to control your custom stage
        ############
        ]

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

        self.x_axis = None

    def commit_settings(self, param):
        """
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()
#        elif ...
        ##

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one detector by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            self.status.update(edict(initialized=False,info="",x_axis=None,y_axis=None,controller=None))
            if self.settings.child(('controller_status')).value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this detector is a slave one')
                else:
                    self.controller = controller
            else:
                ## TODO for your custom plugin
                self.controller = python_wrapper_of_your_instrument()  # any object that will control the stages
                #####################################

            ## TODO for your custom plugin
            # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
            data_x_axis = self.controller.your_method_to_get_the_x_axis() # if possible
            self.x_axis = Axis(data=data_x_axis, label='', units='')
            self.emit_x_axis()


            ## TODO for your custom plugin
            #initialize viewers pannel with the future type of data
            self.data_grabed_signal_temp.emit([DataFromPlugins(name='Mock1',data=[np.array([0.,0.,...]),
                                                                             np.array([0.,0.,...])],
                                                          dim='Data1D', labels=['Mock1', 'label2'],
                                                          x_axis=self.x_axis),])

            ##############################

            self.status.info = "Whatever info you want to log"
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status',[getLineInfo()+ str(e),'log']))
            self.status.info=getLineInfo()+ str(e)
            self.status.initialized=False
            return self.status

    def close(self):
        """
        Terminate the communication protocol
        """
        ## TODO for your custom plugin
        self.controller.your_method_to_terminate_the_communication()
        ##

    def grab_data(self, Naverage=1, **kwargs):
        """

        Parameters
        ----------
        Naverage: (int) Number of hardware averaging
        kwargs: (dict) of others optionals arguments
        """
        ## TODO for your custom plugin

        ##synchrone version (blocking function)
        data_tot = self.controller.your_method_to_start_a_grab_snap()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                          dim='Data1D', labels=['dat0', 'data1'])])
        #########################################################

        ##asynchrone version (non-blocking function with callback)
        self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                  dim='Data1D', labels=['dat0', 'data1'])])

    def stop(self):

        ## TODO for your custom plugin
        self.controller.your_method_to_stop_acquisition()
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################

        return ''
