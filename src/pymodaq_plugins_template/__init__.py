from pathlib import Path
from pymodaq_utils.logger import set_logger  # to be imported by other modules.
from _version import __version__, __version_tuple__, version_tuple, version

from .utils import Config
config = Config()


