"""Behaviour tests of instrument plugins against a fake controller: no hardware, no visible GUI.

Here the harness of ``pymodaq.utils.plugin_testing`` is applied to the example fake plugins of ``example_mock_plugins.py``. To test your own plugin, copy
a test and replace the plugin class and the fake controller, for instance::

    from pymodaq_plugins_<name>.daq_move_plugins.daq_move_<Name> import DAQ_Move_<Name>
    actuator = make_actuator(DAQ_Move_<Name>)   # then monkeypatch the controller class with your fake before ini_stage
"""
import pytest

from pymodaq.utils.plugin_testing import (make_actuator, make_detector, move_abs_and_wait, move_rel_and_wait,
                                          move_home_and_wait, grab_and_wait, assert_units, wait_for_signal,
                                          SignalTimeout)
from example_mock_plugins import DAQ_Move_Fake, DAQ_1DViewer_Fake, DAQ_MultiAxes_Fake


@pytest.fixture
def actuator(qapp):
    plugin = make_actuator(DAQ_Move_Fake)
    assert plugin.initialized
    yield plugin
    plugin.close()


@pytest.fixture
def detector(qapp):
    plugin = make_detector(DAQ_1DViewer_Fake, npts=20)
    assert plugin.initialized
    yield plugin
    plugin.close()


class TestActuator:
    def test_ini_returns_info_and_flag(self, actuator):
        assert isinstance(actuator.init_info, str)
        assert actuator.initialized is True

    def test_value_has_units(self, actuator):
        pos = actuator.get_actuator_value()
        assert pos.units == 'mm'

    def test_move_abs(self, actuator):
        pos = move_abs_and_wait(actuator, 2.5)
        assert pos.value('mm') == pytest.approx(2.5, abs=0.01)
        assert actuator.controller.calls[-1] == ('move_at', 2.5)

    def test_move_rel(self, actuator):
        move_abs_and_wait(actuator, 1.)
        pos = move_rel_and_wait(actuator, 0.5)
        assert pos.value('mm') == pytest.approx(1.5, abs=0.01)

    def test_move_home(self, actuator):
        move_abs_and_wait(actuator, 3.)
        pos = move_home_and_wait(actuator)
        assert pos.value('mm') == pytest.approx(0., abs=0.01)

    def test_other_units_are_converted(self, actuator):
        from pymodaq.utils.data import DataActuator
        pos = move_abs_and_wait(actuator, DataActuator(data=1., units='cm'))  # 1 cm = 10 mm
        assert pos.value('mm') == pytest.approx(10., abs=0.01)

    def test_close_releases_the_controller(self, actuator):
        controller = actuator.controller
        actuator.close()
        assert controller.is_open is False

    def test_slave_axis_uses_the_given_controller(self, qapp):
        master = make_actuator(DAQ_MultiAxes_Fake)
        slave = make_actuator(DAQ_MultiAxes_Fake, controller=master.controller)
        assert slave.controller is master.controller
        move_abs_and_wait(slave, 1.)
        assert master.controller.calls[-1] == ('move_at', 1.)
        slave.close()
        assert master.controller.is_open  # only the master releases the shared controller
        master.close()
        assert not master.controller.is_open


class TestDetector:
    def test_grab_returns_data_with_units(self, detector):
        dte = grab_and_wait(detector)
        assert len(dte) == 1
        assert dte[0].shape == (20,)
        assert_units(dte, 'V')

    def test_close_releases_the_controller(self, detector):
        controller = detector.controller
        detector.close()
        assert controller.is_open is False


def test_harness_times_out_when_nothing_happens(qapp, actuator):
    with pytest.raises(SignalTimeout):
        wait_for_signal(actuator.move_done_signal, lambda: None, timeout_ms=100)
