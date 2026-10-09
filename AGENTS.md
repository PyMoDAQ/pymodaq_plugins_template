# AGENTS.md

Guidance for AI coding assistants (and humans) building on **PyMoDAQ 5.3.x** from this template.
PyMoDAQ is a Qt framework that drives lab experiments: hardware is added through small *plugins*, and PyMoDAQ
provides the GUI, threading, data model, scans and HDF5 saving. Python 3.10 to 3.13.

This repository is a plugin package named `pymodaq_plugins_<name>`. Rename everything that still says `template`
before publishing.

## 1. Choose what to build

Prefer the first option that fits:

1. **Instrument plugin** (`daq_move_plugins/`, `daq_viewer_plugins/`): a new device must appear in the Dashboard.
2. **Dashboard extension** (`extensions/`, class derived from `CustomExt`): a workflow that uses instruments
   (scans, feedback, custom panels, logging). It runs inside the Dashboard and reuses its stable mechanisms for
   instruments: the experiment manager and the state manager (how a Dashboard setup is described, loaded and
   restored; the word "preset" is obsolete), the module manager, control-module threading, shared controllers,
   saving. **If the application drives instruments, build a `CustomExt`, not a `CustomApp`.**
3. **Standalone app** (`app/`, class derived from `CustomApp`): only when the application needs **no
   instruments** (data viewer, analysis, h5 browsing, configuration tools).
4. A plain script, for a one-off sequence that does not need a GUI.

## 2. Workflow

```bash
pip install -e .                 # editable install of this plugin, from the repository root
check_plugin                     # static report on this package (hardware not needed)
check_plugin --fail-on todo -v   # also list every unfinished TODO
pytest                           # template tests (package structure, plugin checks, behaviour against a fake controller)
```

Installing PyMoDAQ itself is a separate matter. A plugin only needs the released packages (`pymodaq`,
`pymodaq_utils`, `pymodaq_data`, `pymodaq_gui`, installed as dependencies). If you also have to modify them, work in a
clone of the PyMoDAQ repository and install the four packages in editable mode with the script at its root, never with
`pip install -e .` inside each package (the script handles the order and the options):

```bash
python install-packages.py -d                 # editable + dev extras, from the PyMoDAQ repository root
python install-packages.py -d -qt pyside6     # choose the Qt backend (pyqt5, pyqt6 or pyside6)
```

Do not consider a task finished until `check_plugin` and `pytest` pass. Do not invent PyMoDAQ APIs: if a method
or attribute is not in the base classes (`DAQ_Move_base`, `DAQ_Viewer_base`, `CustomExt`) or in an existing
plugin, look it up in the installed `pymodaq` package instead of guessing.

## 3. Instrument plugins

File and class names must match: `daq_move_<Name>.py` holds `DAQ_Move_<Name>`; `daq_<N>Dviewer_<Name>.py` holds
`DAQ_<N>DViewer_<Name>` (N = 0, 1, 2 or N). Each file ends with `if __name__ == '__main__': main(__file__)`.

**Actuator** (`DAQ_Move_base`). Override at least `ini_attributes`, `ini_stage`, `get_actuator_value`, `close`,
`commit_settings`, `move_abs`, `move_rel`, `move_home`, `stop_motion`.

- `ini_stage(controller=None)` returns `(info: str, initialized: bool)`. If `self.is_master`, create the controller;
  otherwise store the `controller` passed in (several axes share one controller).
- Class attributes: `is_multiaxes`, `_axis_names`, `_controller_units`, `_epsilons`,
  `data_actuator_type = DataActuatorType.DataActuator`, optionally `ui_type` and `has_encoder`.
- `params` = list of dicts + `comon_parameters_fun(is_multiaxes, axis_names=..., epsilon=...)`.
- Positions are `DataActuator` objects with **units** (`units=self.axis_unit`); use `check_bound`,
  `set_position_with_scaling` and `get_position_with_scaling` as in the template.

**Detector** (`DAQ_Viewer_base`). Override at least `ini_attributes`, `ini_detector`, `grab_data`, `stop`,
`close`, `commit_settings`.

- `ini_detector(controller=None)` returns `(info, initialized)`, same master/slave logic.
- `params = comon_parameters + [...]`.
- Data leaves the plugin as `DataToExport` containing `DataFromPlugins` (with `dim='Data0D'|'Data1D'|'Data2D'|'DataND'`,
  `labels`, `axes=[Axis(...)]`) emitted through `self.dte_signal` (grab) or `self.dte_signal_temp` (live preview).

**Rules that matter**

- Plugin code runs in a worker thread. **Never create or touch Qt widgets** from it. Report progress with
  `self.emit_status(ThreadCommand('Update_Status', ['message']))`.
- Do not block for long inside `grab_data` or a move; use the asynchronous pattern shown in the template and the
  polling that PyMoDAQ already does (`epsilon`).
- Always release the hardware in `close()`, only if `self.is_master`. Leave actuators in a safe state on error.
- Settings are `pyqtgraph` Parameter dicts (`{'title', 'name', 'type', 'value', ...}`). React to changes in
  `commit_settings(param)` by `param.name()`.
- Units are `pint`-based. Give every actuator value and every `Axis` a unit; mismatches raise `DataUnitError`.
- Hardware access code goes in `hardware/`, behind a small wrapper class. This lets the plugin be tested with a
  mock controller and keeps the plugin file readable.
- Defaults live in `resources/config_template.toml`, not in the code. Read configuration values through
  `GlobalConfig` from `pymodaq_utils.config`: a singleton that wraps the `Config` objects of all packages, e.g.
  `GlobalConfig()('gui', 'style', 'theme')`. Do not parse the toml files yourself, and do not instantiate a `Config`
  class directly (deprecated): PyMoDAQ registers the `Config` of `<your_package>/utils.py` in `GlobalConfig` when it
  discovers the plugin, under the package name without `pymodaq_plugins_`.

**Testing behaviour without hardware.** `tests/plugin_harness.py` drives a plugin the way PyMoDAQ does, without a GUI:
`make_actuator` / `make_detector` (instantiate and call `ini_stage` / `ini_detector`), `move_abs_and_wait`,
`move_rel_and_wait`, `move_home_and_wait`, `grab_and_wait` (return the final position or the `DataToExport`, and fail
on a timeout) and `assert_units`. `tests/example_mock_plugins.py` shows a fake controller and the smallest actuator,
multi-axes actuator and 1D detector; `tests/test_plugin_behaviour.py` shows the tests to copy. Write the vendor
communication behind a wrapper class in `hardware/`, write a fake with the same public methods, and run your real
plugin class against it (monkeypatch the wrapper class). Targets reach the plugin in the axis unit, as in PyMoDAQ.

**Legacy patterns to avoid** (older tutorials and models still produce them; `check_plugin` flags several):
`stage_names` (use `_axis_names`), `_epsilon` (use `_epsilons`), `data_actuator_type = float` (use
`DataActuatorType.DataActuator`), the group names `multiaxes` and `multi_status` (now `controller` and
`controller_status`), importing `CustomExt` from `pymodaq.extensions.custom_ext` (use `pymodaq.utils.custom_ext`),
and the deprecated `CustomApp` / `CustomExt` hooks `setup_docks` and `setup_menu` (use `setup_docks_and_widgets` and
`setup_menus_and_toolbars`).

## 4. Dashboard extensions (`CustomExt`)

- Entry point group `pymodaq.extensions` in `pyproject.toml`; each module in `extensions/` defines
  `EXTENSION_NAME` (menu label), `CLASS_NAME` (class name) and a class derived from `CustomExt`.
- Import: `from pymodaq.utils.custom_ext import CustomExt`.
- A plugin extension follows exactly the pattern of the core extensions (`daq_scan`, `sequencer`, `ramping`, data
  mixer). The only difference is `EXTENSION_NAME` and `CLASS_NAME`, which the Dashboard needs to recognise it.
- **`_quit_fun(self) -> bool` must be overridden and return `True`** (return `False`, after telling the user, while
  the extension is running). The base implementation returns `None`, which prevents closing.
- **`main()` pattern** (to run the extension alone, same as the core ones):

  ```python
  def main():
      import sys
      from pymodaq_gui.qt_utils import mkQApp
      from pymodaq.dashboard import load_dashboard_with_arguments
      from pymodaq.utils.gui_utils.loader_utils import create_extension

      app = mkQApp('My Extension')
      win, dashboard, _ = load_dashboard_with_arguments(show_dashboard=False, load_extension=False)
      win.mainwindow.setVisible(False)
      win_ext, ext = create_extension(dashboard, MyExtension, show_extension=True)
      sys.exit(app.exec())
  ```

  `load_dashboard_with_arguments` reads the command line (`-x EXPERIMENT_NAME`, `-s STATE_NAME`).
  `create_extension` already shows the window: do not call `win_ext.show()` again, and do not use `create_load_dashboard`
  here.
- Long-running work (a scan, a sequence, a ramp) goes in an `ExtensionWorker` subclass run in a thread, started and
  stopped from the extension's workflow actions, as in `sequencer.py` and `ramping.py`.
- `__init__(self, parent: DockArea, dashboard)`: call `super().__init__(parent, dashboard)`, then `self.setup_ui()`.
- **Experiment and state belong to the Dashboard.** The *experiment* is the list of instruments (actuators and
  detectors) the Dashboard manages and controls; the *state* is the state of that experiment, mostly the values of the
  instruments' settings and of the Dashboard's actuators. An extension must use the managers it gets through its
  `dashboard` argument, as `self.experiment_manager` and `self.state_manager`, and never create its own, nor its own
  save/load of instrument configurations. Override `do_things_after_experiment_set(experiment_name, show_dashboard)`
  to react when an experiment is set (the base class refreshes `self.modules_manager` there), and use
  `create_dashboard_toolbar(...)` to expose the experiment and state actions in your extension.
- The Dashboard's instruments are reached through `self.modules_manager`. This `ModulesManager` is created anew for
  each extension by the base class `__init__`, so that every extension can handle different instruments: never share
  it between extensions, replace it, or reuse the Dashboard's one. Do not create control modules yourself inside an
  extension, and do not talk to the hardware directly.
- Implement the lifecycle: `setup_docks_and_widgets`, `setup_actions`, `setup_menus_and_toolbars`,
  `connect_things`, `value_changed`, `quit_fun`. `setup_docks` and `setup_menu` are deprecated. The GUI thread runs
  your code; react to module signals, never poll or sleep.

## 5. Standalone apps (`CustomApp`)

Only when no instrument is needed. Same (non-deprecated) lifecycle as above, `parent` is a `DockArea` or `QMainWindow`, and
`main()` creates the app with `mkQApp`. If instruments become necessary, move the logic to a `CustomExt`.

## 6. Done checklist

- [ ] Names (package, files, classes) match and the `template` placeholders are gone.
- [ ] The `[features]` flags at the top of `pyproject.toml` match the folders you use (`instruments`, `extensions`,
      `models`...): entry points are generated only for the features set to `true` (`check_plugin` warns, PMQ109).
- [ ] `check_plugin` passes; no `NotImplementedError` or `TODO` left in the files you wrote.
- [ ] Units set on all actuator values and axes; safe behaviour in `close()` and on errors.
- [ ] Tests added for new behaviour using a mock controller (no real hardware in CI).
- [ ] Docstring of each plugin class states: compatible devices, what was tested, PyMoDAQ and OS versions,
      drivers to install.
- [ ] `README.rst` updated; target PyMoDAQ version stated.
