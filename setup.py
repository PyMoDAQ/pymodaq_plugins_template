import distutils.dir_util
from distutils.command import build
import os, sys, re
try:
    import setuptools
    from setuptools import setup, find_packages
    from setuptools.command import install
except ImportError:
    sys.stderr.write("Warning: could not import setuptools; falling back to distutils.\n")
    from distutils.core import setup
    from distutils.command import install

from pymodaq_plugins.version import get_version

with open('README.rst') as fd:
    long_description = fd.read()

setupOpts = dict(
    name='pymodaq_plugins_custom',
    description='Hardware plugins for PyMoDAQ',
    long_description=long_description,
    license='MIT',
    url='http://pymodaq.cnrs.fr',
    author='Sébastien Weber',
    author_email='sebastien.weber@cemes.fr',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: CeCILL-B Free Software License Agreement (CECILL-B)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        ],)


setup(
    version=get_version(),
    packages=find_packages(),
    package_data={'': ['*.dll']},
    entry_points={'pymodaq.plugins': 'custom = pymodaq_plugins_custom'},
    install_requires=[
        'pymodaq>=2.0',
        ],
    **setupOpts
)

