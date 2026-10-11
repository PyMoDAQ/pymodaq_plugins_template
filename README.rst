pymodaq_plugins_template
########################

.. the following must be adapted to your developed package, links to pypi, github  description...

.. image:: https://img.shields.io/pypi/v/pymodaq_plugins_template.svg
   :target: https://pypi.org/project/pymodaq_plugins_template/
   :alt: Latest Version

.. image:: https://readthedocs.org/projects/pymodaq/badge/?version=latest
   :target: https://pymodaq.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_template/workflows/Upload%20Python%20Package/badge.svg
   :target: https://github.com/PyMoDAQ/pymodaq_plugins_template
   :alt: Publication Status

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_template/actions/workflows/Test.yml/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_template/actions/workflows/Test.yml


Use this template to create a repository on your account and start the development of your own PyMoDAQ plugin!

This branch targets **PyMoDAQ 5.3.x** (Python 3.10 to 3.13). Use the branch matching your PyMoDAQ version.

Development
===========

* Install your plugin in editable mode: ``pip install -e .``
* Check it, without any hardware: ``check_plugin`` (and ``pytest``)
* If you use an AI coding assistant, point it to ``AGENTS.md``: it describes the patterns to follow for instrument
  plugins, Dashboard extensions (``CustomExt``, whenever instruments are involved) and standalone apps
  (``CustomApp``, only if no instruments are needed).


Authors
=======

* First Author  (myemail@xxx.org)
* Other author (myotheremail@xxx.org)

.. if needed use this field

    Contributors
    ============

    * First Contributor
    * Other Contributors

.. if needed use this field

  Depending on the plugin type, delete/complete the fields below


Instruments
===========

Below is the list of instruments included in this plugin

Actuators
+++++++++

* **yyy**: control of yyy actuators
* **xxx**: control of xxx actuators

Viewer0D
++++++++

* **yyy**: control of yyy 0D detector
* **xxx**: control of xxx 0D detector

Viewer1D
++++++++

* **yyy**: control of yyy 1D detector
* **xxx**: control of xxx 1D detector


Viewer2D
++++++++

* **yyy**: control of yyy 2D detector
* **xxx**: control of xxx 2D detector


PID Models
==========


Extensions
==========


Installation instructions
=========================

* PyMoDAQ’s version.
* Operating system’s version.
* What manufacturer’s drivers should be installed to make this plugin run?
