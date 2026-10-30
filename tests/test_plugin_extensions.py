"""Tests of the Dashboard extensions of the plugin, provided by PyMoDAQ (from version 5.3.7).

Each extension of the ``extensions`` folder is loaded in an empty Dashboard and closed. Add the tests of the behaviour of
your extensions in this file, with ``loaded_extension`` (from ``pymodaq.utils.plugin_testing``). Delete this file if your
plugin has no extension.
"""
import importlib.util

import pytest

try:
    available = importlib.util.find_spec('pymodaq.utils.plugin_testing.extension_testing') is not None
except ModuleNotFoundError:  # pymodaq is not installed
    available = False
if not available:
    pytest.skip('The extension checks need PyMoDAQ >= 5.3.7', allow_module_level=True)

from pymodaq.utils.plugin_testing.extension_testing import PluginExtensionChecks


class TestExtensions(PluginExtensionChecks):
    # package_name = 'pymodaq_plugins_xxxx'  # only if it cannot be found from the pyproject.toml and the package folder
    strict_imports = False  # True: an extension that cannot be imported (missing dependency) fails instead of being skipped
