from pathlib import Path
from pymodaq.daq_utils.daq_utils import set_logger

with open(str(Path(__file__).parent.joinpath('VERSION')), 'r') as fvers:
    __version__ = fvers.read().strip()
