"""Template of a Dashboard extension.

An extension is a ``CustomExt``: a small application living inside the Dashboard. Everything related to the
instruments (the experiment, i.e. the list of actuators and detectors, and its state) is handled by the Dashboard,
the extension only uses it through its ``dashboard`` argument:

* ``self.modules_manager``: a ModulesManager created for this extension, giving access to the actuators and
  detectors of the Dashboard's experiment (never create control modules yourself)
* ``self.experiment_manager`` and ``self.state_manager``: the Dashboard's managers, never create your own

The only difference with the extensions of the PyMoDAQ core is the presence of the ``EXTENSION_NAME`` and
``CLASS_NAME`` variables below, needed by the Dashboard to recognize your extension (plus the
``pymodaq.extensions`` entry point in pyproject.toml).
"""
from qtpy import QtWidgets

from pymodaq_gui import utils as gutils
from pymodaq_utils.config import GlobalConfig
from pymodaq_utils.logger import set_logger, get_module_name

from pymodaq.utils.custom_ext import CustomExt

logger = set_logger(get_module_name(__file__))

# all the configurations (PyMoDAQ's packages and the one of your plugin package) are read from GlobalConfig, for
# instance: config('gui', 'style', 'theme')
config = GlobalConfig()

# todo: modify this as you wish
EXTENSION_NAME = 'MY_EXTENSION_NAME'  # the name that will be displayed in the extension list in the
# dashboard
CLASS_NAME = 'CustomExtensionTemplate'  # this should be the name of your class defined below


# todo: modify the name of this class to reflect its application and change the name in the main
# method at the end of the script
class CustomExtensionTemplate(CustomExt):

    # todo: if you wish to create custom Parameter and corresponding widgets. These will be
    # automatically added as children of self.settings. Morevover, the self.settings_tree will
    # render the widgets in a Qtree. If you wish to see it in your app, add is into a Dock
    params = []

    def __init__(self, parent: gutils.DockArea, dashboard):
        super().__init__(parent, dashboard)  # also creates self.modules_manager for this extension

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

    def setup_menus_and_toolbars(self, menubar: QtWidgets.QMenuBar = None):
        """Non mandatory method to be subclassed in order to create menus and toolbars

        Examples
        --------
        >>>file_menu = self.add_menu('file', 'File', parent_menu=menubar)

        See Also
        --------
        pymodaq.utils.managers.action_manager.ActionManager
        """
        # adds the toolbar showing/hiding the Dashboard, loading an experiment and a state
        self.create_dashboard_toolbar(add_break=False)

    def setup_actions(self):
        """Method where to create actions to be subclassed

        Examples
        --------
        >>> self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True)

        See Also
        --------
        ActionManager.add_action
        """
        # todo: replace this example action by yours
        self.add_action('list_modules', 'List modules', 'add_circle',
                        tip='Show the actuators and detectors of the current experiment')

    def connect_things(self):
        """Connect actions and/or other widgets signal to methods"""
        # todo: replace this example by your connections
        self.connect_action('list_modules', self.list_modules)

    def list_modules(self):
        """Example: use the modules_manager to access the instruments of the Dashboard's experiment"""
        self.update_status(f'Actuators: {self.modules_manager.actuators_name}, '
                           f'detectors: {self.modules_manager.detectors_name}')

    def do_things_after_experiment_set(self, experiment_name: str, show_dashboard: bool = None):
        """Called each time an experiment (the list of instruments) has been set in the Dashboard

        The base class updates self.modules_manager with the new instruments.
        """
        super().do_things_after_experiment_set(experiment_name, show_dashboard)
        # todo: update your widgets with the new instruments if needed

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

    def _quit_fun(self) -> bool:
        """Called when the extension is closed. Return True to let it quit, False to refuse (for instance while
        running). The base class returns None, which would prevent the extension from closing.
        """
        return True


def main():
    """Run the extension on its own: loads a Dashboard (hidden), then the extension

    The Dashboard command line options apply, for instance ``-x EXPERIMENT_NAME -s STATE_NAME``
    """
    import sys
    from pymodaq_gui.qt_utils import mkQApp
    from pymodaq.dashboard import load_dashboard_with_arguments
    from pymodaq.utils.gui_utils.loader_utils import create_extension

    app = mkQApp('Custom Ext')

    win, dashboard, _ = load_dashboard_with_arguments(show_dashboard=False,
                                                      load_extension=False,
                                                      )
    win.mainwindow.setVisible(False)

    win_ext, ext = create_extension(dashboard, CustomExtensionTemplate, show_extension=True)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
