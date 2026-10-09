"""Minimal fake controller and plugins used to test the harness, and as a pattern to copy.

When you write a real plugin, keep the vendor communication behind a small wrapper class in ``hardware/`` and write a
fake of that wrapper with the same public methods: tests then run the real plugin class against the fake.
"""
import numpy as np

from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun, DataActuatorType)
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters
from pymodaq.utils.data import DataActuator, DataFromPlugins
from pymodaq_data.data import DataToExport


class FakeController:
    """Stands for the python wrapper of a real instrument: instantaneous, in memory, records what it was asked"""
    def __init__(self):
        self.position = 0.
        self.is_open = True
        self.calls = []

    def move_at(self, value: float):
        self.calls.append(('move_at', value))
        self.position = value

    def get_position(self) -> float:
        return self.position

    def acquire(self, npts: int = 10) -> np.ndarray:
        self.calls.append(('acquire', npts))
        return np.linspace(0., 1., npts)

    def close(self):
        self.is_open = False


class DAQ_Move_Fake(DAQ_Move_base):
    """Smallest actuator following the template: one axis, positions in mm"""
    _controller_units = 'mm'
    is_multiaxes = False
    _axis_names = ['axis']
    _epsilons = [0.01]
    data_actuator_type = DataActuatorType.DataActuator
    params = comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilons)

    def ini_attributes(self):
        self.controller: FakeController = None

    def ini_stage(self, controller=None):
        self.controller = FakeController() if self.is_master else controller
        return 'fake stage ready', True

    def get_actuator_value(self) -> DataActuator:
        pos = DataActuator(data=self.controller.get_position(), units=self.axis_unit)
        return self.get_position_with_scaling(pos)

    def move_abs(self, value: DataActuator):
        value = self.check_bound(value)
        self.target_value = value
        value = self.set_position_with_scaling(value)
        self.controller.move_at(value.value())

    def move_rel(self, value: DataActuator):
        value = self.check_bound(self.current_value + value) - self.current_value
        self.target_value = value + self.current_value
        value = self.set_position_with_scaling(self.target_value)
        self.controller.move_at(value.value())

    def move_home(self):
        self.move_abs(DataActuator(data=0., units=self.axis_unit))

    def stop_motion(self):
        self.controller.calls.append(('stop',))

    def commit_settings(self, param):
        pass

    def close(self):
        if self.is_master:
            self.controller.close()


class DAQ_MultiAxes_Fake(DAQ_Move_Fake):
    """Several axes sharing one controller: the master creates it, the slaves are given it by PyMoDAQ"""
    is_multiaxes = True
    _axis_names = ['x', 'y']
    _epsilons = [0.01, 0.01]
    params = comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilons)


class DAQ_1DViewer_Fake(DAQ_Viewer_base):
    """Smallest 1D detector following the template"""
    params = comon_parameters + [
        {'title': 'Npts:', 'name': 'npts', 'type': 'int', 'value': 10, 'min': 1},
    ]

    def ini_attributes(self):
        self.controller: FakeController = None

    def ini_detector(self, controller=None):
        self.controller = FakeController() if self.is_master else controller
        return 'fake detector ready', True

    def commit_settings(self, param):
        pass

    def grab_data(self, Naverage=1, **kwargs):
        y = self.controller.acquire(self.settings['npts'])
        self.dte_signal.emit(DataToExport(
            name='fake',
            data=[DataFromPlugins(name='trace', data=[y], dim='Data1D', labels=['signal'], units='V')]))

    def close(self):
        if self.is_master:
            self.controller.close()
