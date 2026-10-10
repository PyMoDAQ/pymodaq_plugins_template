"""Template of a standalone application, for applications that need NO instruments.

If your application drives instruments (actuators, detectors), write a Dashboard extension (CustomExt, see the
extensions folder) instead: it relies on the Dashboard's stable mechanisms to handle instruments (experiment and
state managers, modules manager...).
"""
from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_utils.config import GlobalConfig
from pymodaq_utils.logger import set_logger, get_module_name

logger = set_logger(get_module_name(__file__))

# all the configurations (PyMoDAQ's packages and the one of your plugin package) are read from GlobalConfig, for
# instance: config('gui', 'style', 'theme')
config = GlobalConfig()


# todo: modify the name of this class to reflect its application and change the name in the main
# method at the end of the script
class CustomAppTemplate(gutils.CustomApp):

    # todo: if you wish to create custom Parameter and corresponding widgets. These will be
    # automatically added as children of self.settings. Morevover, the self.settings_tree will
    # render the widgets in a Qtree. If you wish to see it in your app, add is into a Dock
    params = []

    def __init__(self, parent: gutils.DockArea):
        super().__init__(parent)

        self.setup_ui()  # calls, in this order: setup_docks_and_widgets, setup_menus_and_toolbars,
        # setup_actions, connect_things and do_things_after_ui_setup

    def setup_docks_and_widgets(self):
        """Method to be subclassed to setup the docks layout

        Examples
        --------
        >>>self.docks['ADock'] = gutils.Dock('ADock name')
        >>>self.dockarea.addDock(self.docks['ADock'])
        >>>self.docks['AnotherDock'] = gutils.Dock('AnotherDock name')
        >>>self.dockarea.addDock(self.docks['AnotherDock'''], 'bottom', self.docks['ADock'])

        See Also
        --------
        pyqtgraph.dockarea.Dock
        """
        # todo: create docks and add them here to hold your widgets. Here the settings tree in a dock
        self.docks['settings'] = gutils.Dock('Settings')
        self.dockarea.addDock(self.docks['settings'])
        self.docks['settings'].addWidget(self.settings_tree)

    def setup_actions(self):
        """Method where to create actions to be subclassed

        Examples
        --------
        >>> self.add_action('quit', 'Quit', 'close2', "Quit program")
        >>> self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True)
        >>> self.add_action('load', 'Load', 'Open', "Load target file (.h5, .png, .jpg) or data from camera"
            , checkable=False)
        >>> self.add_action('save', 'Save', 'SaveAs', "Save current data", checkable=False)

        See Also
        --------
        ActionManager.add_action
        """
        # todo: replace this example action by yours
        self.add_action('say_hello', 'Say hello', 'add_circle', tip='Show a message in the status bar')

    def connect_things(self):
        """Connect actions and/or other widgets signal to methods"""
        # todo: replace this example by your connections
        self.connect_action('say_hello', lambda: self.update_status('Hello'))

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        """Non mandatory method to be subclassed in order to create menus and toolbars

        create menu for actions contained into the self._actions, for instance:

        Examples
        --------
        >>>file_menu = menubar.addMenu('File')
        >>>self.affect_to('load', file_menu)
        >>>self.affect_to('save', file_menu)

        >>>file_menu.addSeparator()
        >>>self.affect_to('quit', file_menu)

        See Also
        --------
        pymodaq.utils.managers.action_manager.ActionManager
        """
        # todo create and populate menu using actions defined above in self.setup_actions
        pass

    def value_changed(self, param):
        """ Actions to perform when one of the param's value in self.settings is changed from the
        user interface

        For instance:
        if param.name() == 'do_something':
            if param.value():
                print('Do something')
                self.settings.child('main_settings', 'something_done').setValue(False)

        Parameters
        ----------
        param: (Parameter) the parameter whose value just changed
        """
        pass


def main():
    from pymodaq_gui.qt_utils import mkQApp
    app = mkQApp('CustomApp')

    mainwindow = QtWidgets.QMainWindow()
    dockarea = gutils.DockArea()
    mainwindow.setCentralWidget(dockarea)

    # todo: change the name here to be the same as your app class
    prog = CustomAppTemplate(dockarea)

    mainwindow.show()

    app.exec()


if __name__ == '__main__':
    main()
