=====================
Installing pyAutoMark
=====================

.. contents::
   :depth: 1
   :local:
   :backlinks: none

.. highlight:: console

Overview
--------

pyAutoMark is written in 
`Python`_ and supports Python 3.8+. It is built
upon the `pytest`_ unit testing framework, 
`openpyxl <https://openpyxl.readthedocs.io/>`_ for reading and writing xlsx files
and uses the `pytest-timeout <https://pypi.org/project/pytest-timeout/>`_ plugin for `pytest`_. 

.. _pytest: https://pytest.org/
.. _Python: https://www.python.org/

Installation
------------

Python is distributed as a Python package and should work on most platforms that support Python.
It has been tested on Both Windows 10 and Ubuntu 

pyAutoMark is published on the `Python Package Index <https://pypi.org/project/pyAutoMark.>`_.  The preferred tool for installing
packages from *PyPI* is :command:`pip`.  This tool is provided with all modern
versions of Python.


On Linux or MacOS, you should open your terminal and run the following command.

::

   $ pip install pyAutoMark

On Windows, you should open *Command Prompt* or *PowerShell* (:kbd:`⊞Win-r` and type
:command:`cmd`) and run the same command.

.. code-block:: doscon

   C:\> pip install pyAutoMark

Installation from source
------------------------

You can install Sphinx directly from a clone of the `Git repository`_.  

.. _Git repository: https://github.com/willijar/pyAutoMark

This can be done either by cloning the repo and installing from the local clone

::

   $ git clone https://github.com/willijar/pyAutoMark
   $ cd pyAutoMark
   $ pip install .

or by simply installing directly via :command:`git`.

::

   $ pip install https://github.com/willijar/pyAutoMark
