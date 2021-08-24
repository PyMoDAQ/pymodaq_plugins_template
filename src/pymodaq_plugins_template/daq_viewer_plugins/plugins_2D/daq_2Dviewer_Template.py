import numpy as np
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters


class DAQ_2DViewer_Template(DAQ_Viewer_base):
    """
    """
    params = comon_parameters + [
        ## TODO for your custom plugin
        # elements to be added here as dicts in order to control your custom stage
        ############
    ]

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

        self.x_axis = None
        self.y_axis = None

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
            self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
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
            data_x_axis = self.controller.your_method_to_get_the_x_axis()  # if possible
            self.x_axis = Axis(data=data_x_axis, label='', units='')
            self.emit_x_axis()

            # get the y_axis (you may want to to this also in the commit settings if y_axis may have changed
            data_y_axis = self.controller.your_method_to_get_the_y_axis()  # if possible
            self.y_axis = Axis(data=data_y_axis, label='', units='')
            self.emit_y_axis()

            ## TODO for your custom plugin
            # initialize viewers pannel with the future type of data
            self.data_grabed_signal_temp.emit([DataFromPlugins(name='Mock1', data=["2D numpy array"],
                                                  dim='Data2D', labels=['dat0'],
                                                  x_axis=self.x_axis,
                                                  y_axis=self.y_axis), ])

            ##############################

            self.status.info = "Whatever info you want to log"
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
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
                                                      dim='Data2D', labels=['dat0'])])
        #########################################################

        ##asynchrone version (non-blocking function with callback)
        self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                      dim='Data2D', labels=['dat0'])])

    def stop(self):

        ## TODO for your custom plugin
        self.controller.your_method_to_stop_acquisition()
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################

        return ''


def main():
    """
    this method start a DAQ_Viewer object with this defined plugin as detector
    Returns
    -------

    """
    import sys
    from PyQt5 import QtWidgets
    from pymodaq.daq_utils.gui_utils import DockArea
    from pymodaq.daq_viewer.daq_viewer_main import DAQ_Viewer
    from pathlib import Path

    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)
    win.resize(1000, 500)
    win.setWindowTitle('PyMoDAQ Viewer')
    detector = Path(__file__).stem[13:]
    det_type = f'DAQ{Path(__file__).stem[4:6].upper()}'
    prog = DAQ_Viewer(area, title="Testing", DAQ_type=det_type)
    win.show()
    prog.detector = detector
    prog.init_det()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()