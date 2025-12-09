# -*- coding: utf-8 -*-
"""
Created the 17/10/2023

@author: Sebastien Weber
"""
import pytest
from pathlib import Path
import importlib
import pkgutil
from collections.abc import Iterable

from pymodaq_data import Q_, Unit


MANDATORY_MOVE_METHODS = ['ini_attributes', 'get_actuator_value', 'close', 'commit_settings',
                          'ini_stage', 'move_abs', 'move_home', 'move_rel', 'stop_motion']
MANDATORY_VIEWER_METHODS = ['ini_attributes', 'grab_data', 'close', 'commit_settings',
                          'ini_detector', ]


def get_package_name():
    here = Path(__file__).parent
    package_name = here.parent.stem
    return package_name

def get_move_plugins():
    pkg_name = get_package_name()
    try:
        move_mod = importlib.import_module(f'{pkg_name}.daq_move_plugins')
        plugin_list = [mod for mod in [mod[1] for mod in
                                       pkgutil.iter_modules([str(move_mod.path.parent)])]
                       if 'daq_move_' in mod]
    except ModuleNotFoundError:
        plugin_list = []
        move_mod = None
    return plugin_list, move_mod


def get_viewer_plugins(dim='0D'):
    pkg_name = get_package_name()
    try:
        viewer_mod = importlib.import_module(f'{pkg_name}.daq_viewer_plugins.plugins_{dim}')

        plugin_list = [mod for mod in [mod[1] for mod in
                                       pkgutil.iter_modules([str(viewer_mod.path.parent)])]
                       if f'daq_{dim}viewer_' in mod]
    except ModuleNotFoundError:
        plugin_list = []
        viewer_mod = None
    return plugin_list, viewer_mod


def test_package_name_ok():
    assert 'pymodaq_plugins_' in get_package_name()[0:16]


def test_imports():
    pkg_name = get_package_name()
    mod = importlib.import_module(pkg_name)
    assert hasattr(mod, 'config')
    assert hasattr(mod, '__version__')
    move_mod = importlib.import_module(f'{pkg_name}', 'daq_move_plugins')
    importlib.import_module(f'{pkg_name}', 'daq_viewer_plugins')
    importlib.import_module(f'{pkg_name}', 'extensions')
    importlib.import_module(f'{pkg_name}', 'models')
    importlib.import_module(f'{pkg_name}.daq_viewer_plugins', 'plugins_0D')
    importlib.import_module(f'{pkg_name}.daq_viewer_plugins', 'plugins_1D')
    importlib.import_module(f'{pkg_name}.daq_viewer_plugins', 'plugins_2D')
    importlib.import_module(f'{pkg_name}.daq_viewer_plugins', 'plugins_ND')


def test_move_inst_plugins_name():
    plugin_list, move_mod = get_move_plugins()
    for plug in plugin_list:
        name = plug.split('daq_move_')[1]
        assert hasattr(getattr(move_mod, plug), f'DAQ_Move_{name}')


def test_move_has_mandatory_methods():
    plugin_list, move_mod = get_move_plugins()
    for plug in plugin_list:
        name = plug.split('daq_move_')[1]
        klass = getattr(getattr(move_mod, plug), f'DAQ_Move_{name}')
        for meth in MANDATORY_MOVE_METHODS:
            assert hasattr(klass, meth)


def test_move_has_correct_units():
    plugin_list, move_mod = get_move_plugins()
    for plug in plugin_list:
        name = plug.split('daq_move_')[1]
        klass = getattr(getattr(move_mod, plug), f'DAQ_Move_{name}')
        if not isinstance(klass._controller_units, list):
            if isinstance(klass._controller_units, dict):
                units = list(klass._controller_units.values())
            elif isinstance(klass._controller_units, str):
                units = [klass._controller_units]
            else:
                raise TypeError(f'{klass._controller_units} is an invalid type')
        else:
            units = klass._controller_units
        for unit in units:
            Unit(unit)  # check if the unit is known from pint


@pytest.mark.parametrize('dim', ('0D', '1D', '2D', 'ND'))
def test_viewer_has_mandatory_methods(dim):
    plugin_list, mod = get_viewer_plugins(dim)
    for plug in plugin_list:
        name = plug.split(f'daq_{dim}viewer_')[1]
        try:
            module = importlib.import_module(f'.{plug}', mod.__package__)
        except Exception:
            break
        klass = getattr(module, f'DAQ_{dim}Viewer_{name}')
        for meth in MANDATORY_VIEWER_METHODS:
            assert hasattr(klass, meth)

def test_compatibility(capsys):
    capsys.disabled()
    try:
        from pymodaq_plugin_manager.compatibility_checker import PyMoDAQPlugin
    except (ModuleNotFoundError, ImportError) as e:
        pytest.fail(f"Please update pymodaq_plugin_manager to a newer version: {e}")

    plugin = PyMoDAQPlugin(get_package_name(), None)
    success = plugin.all_imports_valid()
    msg = '\n'.join(plugin.failed_imports + [''])

    if not success:
        plugin.save_import_report(".")

    assert success, msg
